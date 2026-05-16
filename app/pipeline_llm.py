from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

from app.pipeline import extract_order_id, build_business_context, rule_based_answer
from rag.simple_retriever import retrieve_policy as retrieve_policy_keyword
from app.local_llm import LocalQwenLLM
from app.policy_overrides import apply_policy_overrides
from tools.product_tool import query_product, format_product_info

from rag.sop_card_retriever import (
    retrieve_sop_cards,
    format_sop_cards_for_prompt,
    filter_sop_cards_for_prompt,
    build_sop_card_fallback_reply,
)
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = LocalQwenLLM()
    return _llm


def detect_high_precision_scene_override(user_query: str) -> Optional[str]:
    """
    高置信业务边界覆盖。

    只处理非常稳定的场景边界：
    - 用户问的是退货/七天无理由相关问题；
    - 同时明确问运费/邮费/谁承担/谁出；
    则应走 shipping_fee_policy，而不是 return_exchange。
    """
    q = (user_query or "").replace(" ", "")

    fee_terms = [
        "运费", "邮费", "寄回运费", "退回运费", "退货运费",
        "来回运费", "包邮", "邮费说明",
    ]
    responsibility_terms = [
        "谁承担", "谁出", "谁付", "谁负责", "承担", "自理", "怎么算", "怎么收",
    ]
    return_terms = [
        "退货", "退换货", "七天无理由", "无理由退", "无理由退货", "寄回", "退回",
    ]

    has_fee = any(x in q for x in fee_terms)
    has_resp = any(x in q for x in responsibility_terms)
    has_return = any(x in q for x in return_terms)

    if has_fee and (has_resp or has_return):
        return "shipping_fee_policy"

    return None


def load_policy_by_scene(scene: str) -> dict:
    """
    按 scene 直接加载 SOP 文件，用于高置信 override。
    避免向量检索把“退货运费”误召回到 return_exchange。
    """
    file_name = f"{scene}.md"

    candidate_roots = [
        Path("knowledge_base"),
        Path("data/knowledge_base"),
        Path("policies"),
        Path("docs/knowledge_base"),
    ]

    for root in candidate_roots:
        p = root / file_name
        if p.exists():
            content = p.read_text(encoding="utf-8")
            return {
                "scene": scene,
                "file_name": file_name,
                "content": f"【来源文件】{file_name}\n{content}",
                "chunks": [
                    {
                        "file_name": file_name,
                        "content": content,
                        "score": 1.0,
                        "source": "high_precision_scene_override",
                    }
                ],
                "retriever": "high_precision_scene_override",
            }

    # 兜底：全项目搜索，排除 archive，避免找不到文件。
    for p in Path(".").rglob(file_name):
        parts = set(p.parts)
        if "archive" in parts or ".git" in parts:
            continue
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            return {
                "scene": scene,
                "file_name": file_name,
                "content": f"【来源文件】{file_name}\n{content}",
                "chunks": [
                    {
                        "file_name": file_name,
                        "content": content,
                        "score": 1.0,
                        "source": "high_precision_scene_override",
                    }
                ],
                "retriever": "high_precision_scene_override",
            }

    # 极端兜底：仍走关键词检索，但强制标记 scene，避免程序中断。
    policy = retrieve_policy_keyword(scene)
    policy["scene"] = scene
    policy["file_name"] = file_name
    policy["retriever"] = "high_precision_scene_override_fallback_keyword"
    return policy


def detect_mainline_route_v2_scene(user_query: str):
    """
    复用已有 current_turn_router_v2。
    只返回 scene，不在这里新增关键词规则。
    """
    try:
        from app.current_turn_router_v2 import detect_current_turn_scene_v2
        result = detect_current_turn_scene_v2(user_query)
    except Exception:
        return None

    if not result:
        return None

    if isinstance(result, dict):
        scene = result.get("scene") or result.get("primary_scene")
    else:
        scene = getattr(result, "scene", None) or getattr(result, "primary_scene", None)

    if scene in {None, "", "unknown", "none", "None"}:
        return None

    return scene


def retrieve_policy_auto(user_query: str):
    override_scene = detect_high_precision_scene_override(user_query)
    if override_scene:
        return load_policy_by_scene(override_scene)

    # Mainline integration:
    # 复用已有 current_turn_router_v2，避免旧 keyword policy 对真实客服 query 的售后/退换货偏置。
    route_v2_scene = detect_mainline_route_v2_scene(user_query)

    # Mainline guard:
    # current_turn_router_v2 只接入已验证能修正旧主线偏置的场景；
    # refund/logistics/return_exchange 暂时继续交给 legacy retriever，避免主线回归。
    trusted_route_v2_scenes = {
        "stock_policy",
        "gift_policy",
        "express_policy",
        "shipping_policy",
        "shipping_fee_policy",
        "order_modify_policy",
        "product_qa_policy",
        "quality_issue",
    }

    if route_v2_scene and route_v2_scene in trusted_route_v2_scenes:
        try:
            policy = load_policy_by_scene(route_v2_scene)
            policy["retriever"] = "current_turn_router_v2"
            policy["route_v2_scene"] = route_v2_scene
            return policy
        except Exception:
            pass

    use_vector = os.getenv("USE_VECTOR_RAG", "0") == "1"

    if not use_vector:
        policy = retrieve_policy_keyword(user_query)
        policy = apply_policy_overrides(user_query, policy)
        policy["retriever"] = "keyword"
        return policy

    from rag.vector_retriever import retrieve_policy_vector

    policy = retrieve_policy_vector(user_query, top_k=3)
    policy = apply_policy_overrides(user_query, policy)
    policy["retriever"] = "vector"
    return policy


def retrieve_history_auto(
    user_query: str,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
):
    """
    历史对话检索入口。

    默认不开启，避免影响原有评测。
    需要设置：
        export USE_CONVERSATION_MEMORY=1

    并在调用 answer_with_llm 时传入 user_id/product_id/order_id。
    """
    use_memory = os.getenv("USE_CONVERSATION_MEMORY", "0") == "1"

    if not use_memory:
        return {
            "has_history": False,
            "summary": "历史对话记忆未启用。",
            "messages": [],
            "summaries": [],
            "risk_level": "disabled",
            "risk_reason": "USE_CONVERSATION_MEMORY!=1",
        }

    if not user_id:
        return {
            "has_history": False,
            "summary": "未提供 user_id，无法检索用户历史对话。",
            "messages": [],
            "summaries": [],
            "risk_level": "unknown",
            "risk_reason": "missing_user_id",
        }

    from memory.conversation_retriever import retrieve_conversation_context

    return retrieve_conversation_context(
        user_id=user_id,
        query=user_query,
        product_id=product_id,
        order_id=order_id,
        top_k=5,
    )


def compact_context(context: dict) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2)


def build_business_summary(context: dict) -> str:
    order = context.get("order")
    logistics = context.get("logistics")
    refund = context.get("refund")
    after_sale = context.get("after_sale")
    product = context.get("product")

    lines = []

    if order:
        lines.append("已查询到订单信息，回复中不要再向用户索要订单号。")
        lines.append(f"订单号：{order['order_id']}")
        lines.append(f"商品：{order['product_name']}，规格：{order['sku']}")
        lines.append(f"订单状态：{order['order_status']}")
        lines.append(f"付款时间：{order['pay_time']}")
        lines.append(f"承诺发货时效：付款后 {order['promise_ship_hours']} 小时内")
        lines.append(f"库存状态：{order['stock_status']}")
        lines.append(f"下单金额：{order['order_amount']} 元")
        lines.append(f"当前参考价格：{order['current_price']} 元")

        try:
            diff = float(order["order_amount"]) - float(order["current_price"])
            if diff > 0:
                lines.append(f"价格变化：当前参考价格低于下单金额，差额约 {diff:.2f} 元。")
            elif diff == 0:
                lines.append("价格变化：当前参考价格与下单金额一致，暂未发现差价。")
            else:
                lines.append("价格变化：当前参考价格高于下单金额，不属于降价补差场景。")
        except Exception:
            pass
    else:
        lines.append("未查询到订单信息。如问题需要订单状态，请在回答规则后，引导用户提供订单号。")

    if logistics:
        lines.append(f"物流状态：{logistics['logistics_status']}")
        lines.append(f"物流最新节点：{logistics['latest_node']}")
        lines.append(f"物流更新时间：{logistics['latest_time']}")
        if logistics.get("signed_by"):
            lines.append(f"签收信息：{logistics['signed_by']}")

    if refund:
        lines.append(f"退款状态：{refund['refund_status']}")
        lines.append(f"退款金额：{refund['refund_amount']} 元")
        lines.append(f"退款申请时间：{refund['apply_time']}")
        lines.append(f"预计到账：{refund['expected_arrival']}")
        lines.append(f"支付渠道：{refund['pay_channel']}")

    if after_sale:
        lines.append(f"售后状态：{after_sale['after_sale_status']}")
        lines.append(f"问题类型：{after_sale['issue_type']}")
        lines.append(f"需补充凭证：{after_sale['evidence_required']}")
        lines.append(f"可选处理方案：{after_sale['solution_options']}")

    if product:
        lines.append("已查询到商品中心信息：")
        for line in format_product_info(product).splitlines():
            lines.append(line)

    return "\n".join(f"- {line}" for line in lines)


def build_history_summary(history_context: dict) -> str:
    """
    将历史检索结果转换成 prompt 片段。
    """
    if not history_context or not history_context.get("has_history"):
        return history_context.get("summary", "未检索到相关历史对话。") if history_context else "未检索到相关历史对话。"

    return (
        f"历史风险等级：{history_context.get('risk_level')}\n"
        f"风险原因：{history_context.get('risk_reason')}\n\n"
        f"{history_context.get('summary')}"
    )



def build_description_mismatch_reference_reply(user_query: str, context: dict, history_context: dict | None = None) -> str:
    product = context.get("product")
    order = context.get("order")

    history_high = history_context and history_context.get("risk_level") == "high"

    lines = [
        "抱歉让您有这样的体验，这类情况需要先核实商品页面信息、订单 SKU、历史沟通记录和实际商品/权益情况，避免直接给您错误结论。"
    ]

    if order:
        lines.append(f"我这边已关联到订单 {order.get('order_id')}，商品是「{order.get('product_name')} {order.get('sku')}」。")

    if product:
        attrs = product.get("attributes") or {}
        attr_text = "；".join([f"{k}：{v}" for k, v in attrs.items()])
        if attr_text:
            lines.append(f"当前商品中心记录显示：{attr_text}。")
        if product.get("special_notes"):
            lines.append(f"商品特别说明：{product.get('special_notes')}")

    if history_high:
        lines.append("同时，历史咨询记录显示用户曾就该商品功能/权益向客服确认过，我会把这部分沟通记录一起纳入核实。")
    elif history_context and history_context.get("has_history"):
        lines.append("我也会结合您之前的历史咨询记录一起核对，确认当时沟通内容和当前商品信息是否一致。")

    if any(w in user_query for w in ["食品", "配料", "无糖", "保质期"]):
        lines.append("麻烦您补充商品页面截图、包装配料表照片和订单信息，我会帮您核实页面描述与实物标注是否一致。")
    elif any(w in user_query for w in ["会员", "课程", "权益", "付费", "虚拟"]):
        lines.append("麻烦您补充会员权益页面截图、需要额外付费的课程截图和订单信息，我会帮您核实权益范围是否与页面说明一致。")
    elif any(w in user_query for w in ["降噪", "防水", "蓝牙", "续航", "功能"]):
        lines.append("麻烦您补充商品页面参数截图、实物/功能测试照片或视频，我会帮您核实商品功能说明是否一致。")
    else:
        lines.append("如果方便，请您提供商品页面截图、实物照片/问题视频或相关权益截图，我帮您进一步核实是否属于描述不符。")

    lines.append("如果核实确实存在商品描述、售前答复或权益说明与实际不一致，建议升级人工或售后专员按平台规则进一步处理；在核实前我不会直接承诺退款、赔偿或认定责任。")

    return "\n".join(lines)


def build_required_points(scene: str, context: dict, user_query: str = "", history_context: Optional[dict] = None) -> str:
    order = context.get("order")
    logistics = context.get("logistics")
    after_sale = context.get("after_sale")

    points = []

    if scene == "price_protection":
        points.append("必须明确说这是价保/差价补偿场景。")
        points.append("必须提到操作路径：【订单详情 → 申请价保】。")
        if order:
            points.append("已知订单号，禁止再次索要订单号。")
            try:
                diff = float(order["order_amount"]) - float(order["current_price"])
                if diff > 0:
                    points.append(f"必须提到：下单金额 {order['order_amount']} 元，当前参考价格 {order['current_price']} 元，差额约 {diff:.2f} 元。")
            except Exception:
                pass
        else:
            points.append("如果没有订单号，可以在最后请用户提供订单号和当前商品页面截图。")

    elif scene == "shipping_policy":
        points.append("必须基于订单状态和库存状态回答。")
        if order:
            points.append("已知订单号，禁止再次索要订单号。")
            points.append(f"必须提到订单状态：{order['order_status']}。")
            points.append(f"必须提到库存状态：{order['stock_status']}。")
            points.append("只能说“可以帮您反馈催发货/申请加急”，不能说“已经联系仓库/已经催促成功”。")
        else:
            points.append("没有订单号时，先说明需要订单号查询发货进度。")

    elif scene == "logistics_policy":
        points.append("必须基于物流状态和最新节点回答。")
        if logistics:
            points.append("已知订单号，禁止再次索要订单号。")
            points.append(f"必须提到物流状态：{logistics['logistics_status']}。")
            points.append(f"必须提到最新节点：{logistics['latest_node']}。")
            if logistics.get("signed_by") == "驿站":
                points.append("用户说没收到，不能反问是否收到；应建议核实驿站、取件码、代收点记录。")
        else:
            points.append("没有物流数据时，请用户提供订单号或快递单号。")
            if "驿站" in user_query or "代收" in user_query or "取件" in user_query:
                points.append("用户提到了驿站/代收点，回复必须提到驿站、取件码、代收点记录或快递员派送记录。")

    elif scene == "quality_issue":
        points.append("必须表达歉意。")
        points.append("必须提到上传照片或视频。")
        points.append("必须提到【订单详情 → 申请售后】。")
        if after_sale:
            points.append("已知订单号，禁止再次索要订单号。")
            points.append(f"必须提到售后状态：{after_sale['after_sale_status']}。")
            points.append(f"必须提到需补充凭证：{after_sale['evidence_required']}。")
            points.append(f"必须提到可选处理方案：{after_sale['solution_options']}。")

    elif scene == "return_exchange":
        points.append("必须先回答规则，不能只让用户提供订单号。")
        points.append("必须提到是否影响二次销售。")
        points.append("必须提到吊牌、包装、未清洗、无污渍异味等商品状态。")
        points.append("必须提到【订单详情 → 申请售后】。")
        points.append("如果没有订单号，可以最后请用户提供订单号和商品现状照片。")

    elif scene == "description_mismatch":
        points.append("必须说明会核实商品页面信息、订单 SKU、商品属性或历史客服沟通记录。")
        points.append("必须引导用户提供商品页面截图、实物照片、问题视频或权益截图等凭证。")
        points.append("必须说明如确认描述不符/售前答复不一致，会升级人工或售后专员处理。")
        points.append("不能直接承诺赔偿、退款或认定商家责任。")

    elif scene == "refund_policy":
        points.append("必须说明退款一般原路返回。")
        if context.get("refund"):
            points.append("必须基于退款状态回答，不能让用户重复提供已知信息。")

    else:
        points.append("先安抚用户，再说明处理动作，最后索要必要信息。")

    # 历史对话高风险约束
    if history_context and history_context.get("risk_level") == "high":
        points.append("历史对话显示可能存在售前客服答复与用户当前反馈不一致，必须谨慎处理。")
        points.append("必须提到“我会帮您核实之前的沟通记录/历史咨询记录”，不能直接否认用户。")
        points.append("必须建议用户提供当前问题凭证，必要时升级人工或售后进一步核实。")
        points.append("不能直接承诺赔偿、退款或认定商家责任。")

    points.append("回复控制在 3-6 句话，语气自然，不要列表化。")
    points.append("不得编造规则、故障原因、赔偿承诺或已经执行的处理动作。")

    return "\n".join(f"- {p}" for p in points)


def build_messages(
    user_query: str,
    policy: dict,
    context: dict,
    reference_reply: str,
    history_context: Optional[dict] = None,
    platform_rule_context: str = "无",
):
    scene = policy["scene"]
    business_summary = build_business_summary(context)
    history_summary = build_history_summary(history_context or {})
    required_points = build_required_points(scene, context, user_query, history_context)

    system_prompt = """你是一个专业、礼貌、稳妥的中文电商客服。
你不是自由创作模型，而是基于业务事实、客服SOP和平台官方规则生成稳妥回复的客服助手。
你必须优先遵守【业务事实摘要】和【平台官方规则参考】。
【事实正确的参考回复】是基础底稿，可以润色；如果平台官方规则更明确，允许基于平台官方规则修正参考回复。
不能添加没有依据的新事实。
如果存在历史对话上下文，必须结合历史信息谨慎回复。"""

    user_prompt = f"""【用户原始问题】
{user_query}

【识别到的业务场景】
{scene}

【检索方式】
{policy.get("retriever", "keyword")}

【命中的客服SOP文件】
{policy.get("file_name", "")}

【业务事实摘要，必须优先使用】
{business_summary}

【历史对话上下文】
{history_summary}

【客服SOP】
{policy["content"]}

【平台官方规则参考】
{platform_rule_context}

【事实正确的参考回复】
{reference_reply}

【本次回复必须满足】
{required_points}

请只输出最终客服回复。
要求：
1. 可以把参考回复润色得更自然。
2. 不要改变业务事实；如果参考回复与平台官方规则不一致，以平台官方规则为准。
3. 不要遗漏“必须满足”的信息。
4. 如果订单号已知，不要再索要订单号。
5. 用户已经说“没收到”时，不要再问“是否收到”。
6. 如果历史对话显示存在售前承诺争议，要表达会核实历史沟通记录，不要直接否认用户。
7. 不要输出标题、分析过程或项目符号。
8. 不要在最终客服回复中暴露 chunk_id、来源级别、检索细节或内部规则编号。
9. 不要输出标题、分析过程或项目符号。"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def validate_reply(
    scene: str,
    reply: str,
    context: dict,
    user_query: str = "",
    history_context: Optional[dict] = None,
) -> tuple[bool, list[str]]:
    errors = []
    order = context.get("order")
    logistics = context.get("logistics")
    after_sale = context.get("after_sale")

    if order and ("提供一下订单号" in reply or "提供订单号" in reply or "请提供订单号" in reply):
        errors.append("已知订单号但回复仍在索要订单号")

    forbidden_phrases = [
        "已经联系仓库",
        "已经催促成功",
        "系统故障",
        "一定赔偿",
        "一定退款",
        "退货重拍",
    ]
    for phrase in forbidden_phrases:
        if phrase in reply:
            errors.append(f"包含禁止表达：{phrase}")

    if scene == "price_protection":
        if "价保" not in reply and "差价" not in reply:
            errors.append("价保场景未提到价保或差价")
        if order:
            try:
                diff = float(order["order_amount"]) - float(order["current_price"])
                if diff > 0:
                    for value in [str(int(order["order_amount"])), str(int(order["current_price"])), str(int(diff))]:
                        if value not in reply:
                            errors.append(f"价保场景遗漏金额信息：{value}")
            except Exception:
                pass

    if scene == "logistics_policy":
        if logistics and logistics.get("signed_by") == "驿站":
            if "驿站" not in reply and "代收" not in reply:
                errors.append("驿站代收场景未提到驿站或代收")
            if "是否已经收到" in reply or "是否收到" in reply:
                errors.append("用户已说明未收到，回复却反问是否收到")
        if not logistics and ("驿站" in user_query or "代收" in user_query or "取件" in user_query):
            if "驿站" not in reply and "代收" not in reply and "取件" not in reply:
                errors.append("用户提到驿站/代收点，但回复未保留该关键业务点")

    if scene == "quality_issue":
        if "照片" not in reply and "视频" not in reply:
            errors.append("质量问题未提到照片或视频")
        if "售后" not in reply:
            errors.append("质量问题未提到售后")
        if after_sale:
            if after_sale["after_sale_status"] not in reply:
                errors.append("质量问题遗漏售后状态")

    if scene == "return_exchange":
        if "二次销售" not in reply:
            errors.append("退换货场景未提到二次销售")
        if "吊牌" not in reply and "包装" not in reply:
            errors.append("退换货场景未提到吊牌或包装")
        if "售后" not in reply:
            errors.append("退换货场景未提到售后")

    if history_context and history_context.get("risk_level") == "high":
        if not any(w in reply for w in ["历史", "之前", "沟通记录", "咨询记录"]):
            errors.append("历史高风险场景未提到核实历史沟通/咨询记录")
        if not any(w in reply for w in ["核实", "确认", "售后", "人工"]):
            errors.append("历史高风险场景未给出核实/售后/人工处理方向")


    # 通用截断检测：模型输出如果没有正常结束符，通常是 max_new_tokens 不够导致被截断
    stripped_reply = reply.strip()
    if stripped_reply and not stripped_reply.endswith(("。", "！", "？", "~", "～", ".", "!", "?", "）", "】")):
        errors.append("回复疑似被截断")

    return len(errors) == 0, errors



def repair_quality_issue_pending_evidence_reply(
    final_reply: str,
    scene: str = None,
    llm_reply: str = None,
    business_context: dict = None,
) -> str:
    """
    修复质量问题订单场景下，最终回复丢失“待用户补充凭证”状态的问题。

    触发条件：
    - scene == quality_issue
    - LLM 回复或业务上下文中包含“待用户补充凭证”
    - final_reply 本身没有包含“待用户补充凭证”

    这是订单事实状态修复，不是单样本关键词补丁。
    """
    final_reply = final_reply or ""
    scene = scene or ""
    llm_reply = llm_reply or ""

    context_text = ""
    if business_context is not None:
        context_text = str(business_context)

    evidence_text = " ".join([llm_reply, context_text, final_reply])

    if scene != "quality_issue":
        return final_reply

    if "待用户补充凭证" not in evidence_text:
        return final_reply

    if "待用户补充凭证" in final_reply:
        return final_reply

    return (
        "您好，已为您查看到该订单当前售后状态为“待用户补充凭证”。"
        "麻烦您在售后页面补充商品整体照片、问题细节照片或视频、订单截图等材料，"
        "我这边会结合订单、商品情况和您提交的凭证继续核实。"
        "提交后请耐心等待售后审核结果，具体处理方式以售后页面核实为准。"
    )


def answer_with_llm(
    user_query: str,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
):
    order_id = extract_order_id(user_query)
    policy = retrieve_policy_auto(user_query)
    context = build_business_context(order_id)

    if product_id:
        context["product"] = query_product(product_id)

    history_context = retrieve_history_auto(
        user_query=user_query,
        user_id=user_id,
        product_id=product_id,
        order_id=order_id,
    )

    raw_reference_reply = rule_based_answer(user_query, policy, context)
    if policy["scene"] == "description_mismatch":
        raw_reference_reply = build_description_mismatch_reference_reply(user_query, context, history_context)

    scoped_sop_cards = retrieve_sop_cards(
        query=user_query,
        scene=policy.get("scene"),
        top_k=3,
    )

    global_sop_cards = retrieve_sop_cards(
        query=user_query,
        scene=None,
        top_k=3,
    )

    sop_cards = scoped_sop_cards
    sop_card_scene_corrected = False

    scoped_top_score = float(scoped_sop_cards[0].get("score", 0)) if scoped_sop_cards else 0.0
    scoped_top_authority = scoped_sop_cards[0].get("authority", "") if scoped_sop_cards else ""

    global_top_score = float(global_sop_cards[0].get("score", 0)) if global_sop_cards else 0.0
    global_top_authority = global_sop_cards[0].get("authority", "") if global_sop_cards else ""
    global_top_scene = global_sop_cards[0].get("scene") if global_sop_cards else None

    # 数据驱动的 SOP Card 场景纠偏：
    # 如果当前 scene 下只命中低分或非官方卡片，而全局检索命中明显更高分的官方 SOP Card，
    # 则使用全局 SOP Card，并同步修正本轮 policy scene。
    if (
        global_sop_cards
        and global_top_authority in {"official_public", "official_api_doc"}
        and global_top_score >= 20
        and (
            not scoped_sop_cards
            or scoped_top_authority not in {"official_public", "official_api_doc"}
            or global_top_score >= scoped_top_score * 2
        )
    ):
        sop_cards = global_sop_cards
        if global_top_scene and global_top_scene != policy.get("scene"):
            # Phase 13F fix:
            # SOP Card global retrieval can provide reference cards, but must not override
            # the main policy scene selected by policy/file retrieval.
            # Otherwise we get inconsistent states such as:
            #   policy_file=price_protection.md, scene=logistics_policy
            policy = dict(policy)
            policy["sop_card_suggested_scene"] = global_top_scene
            sop_card_scene_corrected = False

    # 兼容旧调试字段名，后续可以统一改成 sop_cards
    platform_rule_chunks = sop_cards

    prompt_sop_cards = filter_sop_cards_for_prompt(
        user_query,
        sop_cards,
        policy_scene=policy.get("scene"),
        top_k=3,
    )


    # Phase16Pre-O：
    # metadata gate 只作用于即将进入 prompt 的 SOP 候选。
    # 不修改 retrieval 结果，不修改 sop_cards，不修改 platform_rule_chunks，
    # 不修改向量索引，也不修改生产 SOP 文件。
    metadata_gate_result = {
        "mode": "off",
        "enabled": False,
        "error": None,
        "debug": {
            "prompt_card_count_input": len(prompt_sop_cards or []),
            "prompt_card_count_allowed": len(prompt_sop_cards or []),
            "prompt_card_count_blocked": 0,
            "prompt_card_count_demoted": 0,
            "prompt_card_count_scene_only": 0,
            "prompt_card_count_legacy_unreviewed": 0,
        },
        "gate_annotations": [],
    }

    try:
        from data_tools.sop_metadata_gate import (
            env_gate_enabled,
            env_gate_mode,
            load_card_policy,
            apply_metadata_gate_to_prompt_cards,
        )

        if env_gate_enabled():
            policy_by_id = load_card_policy()
            metadata_gate_result = apply_metadata_gate_to_prompt_cards(
                prompt_cards=prompt_sop_cards,
                policy_by_id=policy_by_id,
                mode=env_gate_mode(),
            )
            metadata_gate_result["enabled"] = True

            # shadow 模式：只记录不拦截。
            # guarded 模式：只保留允许进入 prompt 的 SOP。
            prompt_sop_cards = metadata_gate_result.get(
                "allowed_prompt_cards",
                prompt_sop_cards,
            )

    except Exception as exc:
        # 出错时 fail open，回到旧逻辑。
        # metadata gate 不能影响客服回复主流程可用性。
        metadata_gate_result = {
            "mode": "error_fallback",
            "enabled": False,
            "error": str(exc),
            "debug": {
                "prompt_card_count_input": len(prompt_sop_cards or []),
                "prompt_card_count_allowed": len(prompt_sop_cards or []),
                "prompt_card_count_blocked": 0,
                "prompt_card_count_demoted": 0,
                "prompt_card_count_scene_only": 0,
                "prompt_card_count_legacy_unreviewed": 0,
            },
            "gate_annotations": [],
        }

    platform_rule_context = format_sop_cards_for_prompt(prompt_sop_cards)

    messages = build_messages(
        user_query,
        policy,
        context,
        raw_reference_reply,
        history_context,
        platform_rule_context=platform_rule_context,
    )

    llm = get_llm()
    llm_reply = llm.chat(messages)

    passed, errors = validate_reply(policy["scene"], llm_reply, context, user_query, history_context)

    sop_card_direct_used = False
    sop_card_direct_reply = None

    if prompt_sop_cards:
        top_card = prompt_sop_cards[0]
        top_score = float(top_card.get("score", 0))
        top_authority = top_card.get("authority", "")

        # 数据驱动的高置信 SOP Card 回复：
        # 只允许 prompt eligible cards 进入 direct fallback，避免高风险平台卡跨场景覆盖。
        top_scene = top_card.get("scene", "")

        if (
            top_authority in {"official_public", "official_api_doc"}
            and top_score >= 20
            and (not top_scene or top_scene == policy.get("scene"))
        ):
            sop_card_direct_reply = build_sop_card_fallback_reply(prompt_sop_cards)

    if passed:
        final_reply = llm_reply
        fallback_used = False
    elif sop_card_direct_reply:
        final_reply = sop_card_direct_reply
        fallback_used = True
        sop_card_direct_used = True
    else:
        final_reply = raw_reference_reply

        # description_mismatch 的 raw_reference_reply 已经包含历史沟通核实、商品中心属性、
        # 凭证要求、人工/售后升级和不承诺赔偿，因此不要再额外包一层，避免重复。
        if history_context.get("risk_level") == "high" and policy["scene"] != "description_mismatch":
            final_reply = (
                "抱歉让您有这样的体验。我会先帮您核实之前的历史咨询记录和当前商品情况，避免直接给您错误结论。\\n"
                + raw_reference_reply
                + "\\n如果确认历史答复与商品实际信息不一致，建议进一步升级人工或售后专员核实处理。"
            )

        fallback_used = True

    final_reply = repair_quality_issue_pending_evidence_reply(
        final_reply=final_reply,
        scene=policy.get("scene"),
        llm_reply=llm_reply,
        business_context=context,
    )

    llm_validation_errors = list(errors)
    final_validation_errors = [] if sop_card_direct_used else errors

    return {
        "order_id": order_id,
        "user_id": user_id,
        "product_id": product_id,
        "scene": policy["scene"],
        "retriever": policy.get("retriever", "keyword"),
        "policy_file": policy.get("file_name", ""),
        "retrieved_chunks": policy.get("chunks", []),
        "business_context": context,
        "business_summary": build_business_summary(context),
        "history_context": history_context,
        "history_summary": build_history_summary(history_context),
        "reference_reply": raw_reference_reply,
        "llm_reference_reply": raw_reference_reply,
        "llm_reply": llm_reply,
        "reply": final_reply,
        "fallback_used": fallback_used,
        "sop_card_direct_used": sop_card_direct_used,
        "sop_card_scene_corrected": sop_card_scene_corrected,
        "metadata_gate": metadata_gate_result,
        "original_scene": policy.get("original_scene", policy.get("scene")),
        "validation_errors": final_validation_errors,
        "llm_validation_errors": llm_validation_errors,
        "sop_cards": [
            {
                "chunk_id": x.get("chunk_id"),
                "source_title": x.get("source_title"),
                "scene": x.get("scene"),
                "score": x.get("score"),
                "authority": x.get("authority"),
                "customer_summary": x.get("customer_summary"),
                "next_action": x.get("next_action"),
            }
            for x in sop_cards
        ],
        "platform_rule_chunks": [
            {
                "chunk_id": x.get("chunk_id"),
                "source_title": x.get("source_title"),
                "scene": x.get("scene"),
                "score": x.get("score"),
                "authority": x.get("authority"),
            }
            for x in platform_rule_chunks
        ],
        "retrieved_policy": policy["content"],
        "messages": messages,
    }
