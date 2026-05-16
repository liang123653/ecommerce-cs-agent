import os
# -*- coding: utf-8 -*-
"""
Answer Strategy Orchestrator

目标：
1. 不替代 answer_with_llm；
2. 只在进入主线前判断“是否需要 SOP/业务事实”；
3. 低信息、寒暄、商品知识、常识问题不强行套平台规则；
4. SOP/订单/物流/退款/售后类问题继续调用 app.pipeline_llm.answer_with_llm。
"""

import json
import re
from typing import Any, Dict, Optional


STRATEGIES = {
    "SOP_REQUIRED",
    "FACT_REQUIRED",
    "PRODUCT_KNOWLEDGE",
    "COMMON_SENSE",
    "LOW_INFO",
    "SMALL_TALK",
    "RISK_HANDOFF",
}


# 这里不是关键词规则，而是把已有 scene taxonomy 映射为 answer strategy。
# scene 的产生仍复用 current_turn_router_v2 / 主线已有路由结果。
SCENE_TO_STRATEGY = {
    "refund_policy": "SOP_REQUIRED",
    "return_exchange": "SOP_REQUIRED",
    "quality_issue": "SOP_REQUIRED",
    "shipping_fee_policy": "SOP_REQUIRED",
    "express_policy": "SOP_REQUIRED",
    "invoice_policy": "SOP_REQUIRED",
    "price_protection": "SOP_REQUIRED",
    "description_mismatch": "SOP_REQUIRED",
    "missing_package_policy": "SOP_REQUIRED",
    "promotion_policy": "SOP_REQUIRED",
    "coupon_policy": "SOP_REQUIRED",
    "gift_policy": "SOP_REQUIRED",

    "shipping_policy": "FACT_REQUIRED",
    "logistics_policy": "FACT_REQUIRED",
    "order_modify_policy": "FACT_REQUIRED",

    "product_qa_policy": "PRODUCT_KNOWLEDGE",
    "stock_policy": "PRODUCT_KNOWLEDGE",
    "bulk_purchase_policy": "PRODUCT_KNOWLEDGE",

    "complaint_policy": "RISK_HANDOFF",
}


def _safe_json_loads(text: str) -> Dict[str, Any]:
    if not text:
        return {}

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}

    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def classify_answer_strategy(query: str) -> Dict[str, Any]:
    """
    用 LLM 做语义策略分类，不在这里维护业务关键词表。

    返回：
    {
      "strategy": "...",
      "reason": "...",
      "need_mainline": true/false
    }
    """
    query = (query or "").strip()

    if not query:
        context_fallback = maybe_apply_context_aware_fallback(
            query=query,
            strategy="LOW_INFO",
            original_reply=None,
            user_id=user_id,
            product_id=product_id,
        )
        if context_fallback is not None:
            return context_fallback

        return {
            "strategy": "LOW_INFO",
            "reason": "empty query",
            "need_mainline": False,
        }

    # 极少数稳定低信息/寒暄先处理，避免无意义短句触发主线。
    stable = _fallback_strategy(query)
    if stable.get("reason") in {"fallback_low_info", "fallback_small_talk"}:
        return stable

    # 复用已有 route_v2：如果已有路由能识别 scene，则先映射为 answer strategy。
    routed = _existing_route_strategy(query)
    if routed:
        return routed

    try:
        from app.pipeline_llm import get_llm


        llm = get_llm()

        prompt = f"""
你是电商客服系统的策略路由器，只判断用户问题应该采用哪种回答策略。

只能从以下策略中选一个：
1. SOP_REQUIRED：需要平台规则/SOP约束的问题，例如退款规则、七天无理由、延迟发货、质量售后、运费规则。
2. FACT_REQUIRED：必须查询订单、物流、退款、售后状态才能回答的问题。
3. PRODUCT_KNOWLEDGE：商品知识、商品规格、保存方式、保质期、口味、成分、使用方式、商家商品信息。
4. COMMON_SENSE：生活常识，可以用稳妥常识回答，不需要平台规则。
5. LOW_INFO：信息太少，无法判断，需要追问。
6. SMALL_TALK：寒暄、感谢、结束语。
7. RISK_HANDOFF：投诉、辱骂、举报、赔偿争议、明显高风险，需要安抚并转人工/升级。

要求：
- 不要把所有问题都强行归入平台 SOP。
- 商品知识和生活常识不要强行归为退货/退款/物流。
- 只输出 JSON，不要解释。

用户问题：
{query}

输出格式：
{{"strategy":"...", "reason":"...", "need_mainline":true}}
""".strip()

        raw = llm.chat([
            {
                "role": "system",
                "content": "你只输出合法 JSON。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ])

        data = _safe_json_loads(raw)
        strategy = data.get("strategy")

        if strategy not in STRATEGIES:
            return _fallback_strategy(query)

        need_mainline = strategy in {"SOP_REQUIRED", "FACT_REQUIRED"}

        return {
            "strategy": strategy,
            "reason": data.get("reason") or "llm_strategy_classifier",
            "need_mainline": need_mainline,
            "raw": raw,
        }

    except Exception as e:
        data = _fallback_strategy(query)
        data["reason"] = f"fallback_after_classifier_error:{type(e).__name__}"
        return data



def _existing_route_strategy(query: str):
    """
    复用已有 current_turn_router_v2 / mainline route enhancement。
    不在这里维护用户表达关键词，只把已有 scene 映射成 answer strategy。
    """
    scene = None

    try:
        from app.pipeline_llm import detect_mainline_route_v2_scene
        scene = detect_mainline_route_v2_scene(query)
    except Exception:
        scene = None

    if not scene:
        try:
            from app.current_turn_router_v2 import detect_current_turn_scene_v2
            result = detect_current_turn_scene_v2(query)
            if isinstance(result, dict):
                scene = result.get("scene") or result.get("primary_scene")
            else:
                scene = getattr(result, "scene", None) or getattr(result, "primary_scene", None)
        except Exception:
            scene = None

    if not scene:
        return None

    strategy = SCENE_TO_STRATEGY.get(scene)
    if not strategy:
        return None

    return {
        "strategy": strategy,
        "reason": f"existing_route_v2_scene:{scene}",
        "need_mainline": strategy in {"SOP_REQUIRED", "FACT_REQUIRED"},
        "route_scene": scene,
    }


def _fallback_strategy(query: str) -> Dict[str, Any]:
    """
    兜底只处理极少数明显情况，避免 LLM 分类失败时系统不可用。
    这里不是主路由，不承担复杂业务分类。
    """
    q = (query or "").strip()

    # stable_small_talk_before_low_info:
    # 稳定寒暄/结束语优先于低信息短句，避免“谢谢”被追问。
    if q in {"谢谢", "好的谢谢", "辛苦了", "不用了", "麻烦你了"}:

        return {
            "strategy": "SMALL_TALK",
            "reason": "fallback_small_talk",
            "need_mainline": False,
        }

    if len(q) <= 2:
        return {
            "strategy": "LOW_INFO",
            "reason": "fallback_low_info",
            "need_mainline": False,
        }

    if q in {"谢谢", "好的", "好", "嗯", "不用了", "没事了", "辛苦了"}:
        return {
            "strategy": "SMALL_TALK",
            "reason": "fallback_small_talk",
            "need_mainline": False,
        }

    return {
        "strategy": "SOP_REQUIRED",
        "reason": "fallback_to_mainline",
        "need_mainline": True,
    }


def _reply_low_info(query: str) -> str:
    return "您好，请您再补充一下具体想咨询的问题，我好继续帮您处理。"


def _reply_small_talk(query: str) -> str:
    return "不客气的，有需要您随时联系我。"




def _reply_risk_handoff(query: str) -> str:
    return (
        "非常抱歉给您带来不好的体验，我先帮您记录这个情况。"
        "涉及投诉、赔付或责任认定的问题，需要结合订单、凭证和平台处理结果进一步核实，"
        "我建议为您转人工客服继续处理。"
    )



def _sanitize_product_fact_reply(reply: str) -> str:
    """
    商品事实回复安全收束。

    只处理输出安全，不做用户意图关键词路由：
    - 不泄露内部 provider / mock / TrueFalse；
    - 不把库存数量说成固定承诺；
    - 不使用“放心购买/保证/一定”等过度承诺；
    - 用更自然的页面/外包装兜底口径。
    """
    import re

    reply = (reply or "").strip()

    # 去掉可能残留的内部标记行
    lines = []
    for line in reply.splitlines():
        if "product_fact_provider" in line:
            continue
        if "mock_product_center" in line:
            continue
        if "provider" in line or "mock" in line:
            continue
        lines.append(line)
    reply = "\n".join(lines).strip()

    # 程序值和过度承诺收束
    replacements = {
        "True": "是",
        "False": "否",
        "放心购买": "以页面展示为准",
        "保证": "建议以页面展示为准",
        "一定": "一般",
    }
    for old, new in replacements.items():
        reply = reply.replace(old, new)

    # 库存数量不要变成强承诺。把“还有82件”这类话术收束为“当前显示有库存”。
    reply = re.sub(
        r"目前我们还有\d+件([^，。]*)在售[，,]?",
        r"商品中心当前显示\1还有库存，",
        reply,
    )
    reply = re.sub(
        r"还有\d+件([^，。]*)在售[，,]?",
        r"当前显示\1还有库存，",
        reply,
    )

    # 避免旧版过宽兜底句反复出现
    old_caution = "具体批次、库存和页面信息可能会有变化，建议以商品详情页、下单页或收到商品外包装标注为准。"
    reply = reply.replace(old_caution, "").strip()

    # 更通用、更自然的兜底句
    caution = "具体请以商品详情页、下单页展示或收到商品外包装标注为准。"
    if caution not in reply:
        reply = reply.rstrip("。") + "。" + caution

    return reply

def _reply_product_or_common(query: str, strategy: str) -> str:
    """
    商品知识 / 常识类回复。

    设计原则：
    1. 商品知识类优先查 product_fact_provider。
    2. 查到事实时，允许 LLM 基于事实生成自然回复。
    3. 查不到事实时，不能让 LLM 编商品参数、库存、材质、价格、赠品、配送承诺。
    4. COMMON_SENSE 默认不做业务承诺，避免自由生成造成客服风险。
    """
    if strategy == "PRODUCT_KNOWLEDGE":
        try:
            from app.product_fact_provider import find_product_fact, build_product_fact_context
            from app.pipeline_llm import get_llm

            product_fact = find_product_fact(query)
            product_fact_context = build_product_fact_context(product_fact)

            if product_fact_context:
                llm = get_llm()
                prompt = f"""
你是专业、礼貌、稳妥的中文电商客服。

请只基于【商品事实】回答【用户问题】。

要求：
1. 只回答用户问到的内容，不要把所有商品字段都列出来。
2. 不要输出内部字段名、JSON、工具名、mock、provider、True/False 等程序信息。
3. 涉及保质期、保存方式、库存、发货能力时，提醒以商品详情页、订单页或外包装标注为准。
4. 不要套用退货、退款、物流 SOP。
5. 回复 2-4 句话，语气自然，可以直接发给用户。

【商品事实】
{product_fact_context}

【用户问题】
{query}
""".strip()

                reply = llm.chat([
                    {
                        "role": "system",
                        "content": "你是专业、礼貌、稳妥的中文电商客服。只输出最终客服回复。",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ])

                reply = (reply or "").strip()
                if reply:
                    return _sanitize_product_fact_reply(reply)

        except Exception:
            pass

        # 查不到商品事实时，不允许 LLM 编商品属性。
        return (
            "您好，这个商品信息我这边暂时没有查到准确的商品事实。"
            "为了避免说错参数、库存、材质或活动信息，麻烦您发一下商品链接、商品名称或规格截图，"
            "我再帮您按页面信息核实。"
        )

    # COMMON_SENSE 不再自由生成业务承诺。
    # 真实客服里很多 COMMON_SENSE 实际是缺商品/订单/上下文的业务短句，
    # 如果直接让 LLM 回答，容易编造价格、赠品、库存、材质、自提、发货等事实。
    return (
        "您好，这个问题需要结合具体商品、订单或店铺配置确认。"
        "我这边不能在未核实的情况下直接承诺价格、赠品、库存、材质、配送或售后结果。"
        "麻烦您补充一下商品链接、订单号或具体需求，我再帮您核实。"
    )

def maybe_apply_context_aware_fallback(
    query: str,
    strategy: str,
    original_reply: str,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Guarded context-aware fallback v2.

    Feature flags:
    - USE_CONVERSATION_MEMORY=1
    - USE_CONTEXT_AWARE_FALLBACK=1

    只处理早退类策略，不强制进入旧 mainline。
    """
    if os.getenv("USE_CONTEXT_AWARE_FALLBACK", "0") != "1":
        return None

    if os.getenv("USE_CONVERSATION_MEMORY", "0") != "1":
        return None

    if not user_id:
        return None

    from app.pipeline_llm import retrieve_history_auto
    from app.context_aware_fallback import (
        should_use_context_aware_fallback,
        build_context_fallback_result,
    )

    history_context = retrieve_history_auto(
        user_query=query,
        user_id=user_id,
        product_id=product_id,
        order_id=None,
    )

    if not should_use_context_aware_fallback(strategy, history_context):
        return None

    return build_context_fallback_result(
        query=query,
        strategy=strategy,
        original_reply=original_reply,
        history_context=history_context,
        product_id=product_id,
    )


def answer_with_strategy(query: str, user_id: Optional[str] = None, product_id: Optional[str] = None) -> Dict[str, Any]:
    """
    对外入口：
    - SOP/事实类：调用原主线 answer_with_llm；
    - 非 SOP 类：直接生成合理客服回复；
    - 返回 trace，便于 demo/eval。
    """
    # Fast path:
    # 对“已有历史 + 高风险多轮承接”场景，先走 context-aware fallback。
    # 这样可以避免为了分类而额外调用大模型。
    # 注意：只在显式开启 USE_CONTEXT_AWARE_FALLBACK_FAST=1 时生效。
    if (
        os.getenv("USE_CONVERSATION_MEMORY", "0") == "1"
        and os.getenv("USE_CONTEXT_AWARE_FALLBACK", "0") == "1"
        and os.getenv("USE_CONTEXT_AWARE_FALLBACK_FAST", "0") == "1"
        and user_id
    ):
        try:
            from app.pipeline_llm import retrieve_history_auto
            from app.context_aware_fallback import (
                build_context_fallback_result,
                has_high_risk_summary_tag,
            )

            history_context = retrieve_history_auto(
                user_query=query,
                user_id=user_id,
                product_id=product_id,
                order_id=None,
            )

            if (
                history_context
                and history_context.get("has_history")
                and (
                    history_context.get("risk_level") == "high"
                    or has_high_risk_summary_tag(history_context)
                )
            ):
                fast_result = build_context_fallback_result(
                    query=query,
                    strategy="CONTEXT_AWARE_FALLBACK",
                    original_reply="",
                    history_context=history_context,
                    product_id=product_id,
                )
                fast_result["query"] = query
                fast_result["strategy_reason"] = "pre_strategy_high_risk_history_context"
                fast_result["need_mainline"] = False
                return fast_result
        except Exception:
            pass

    strategy_info = classify_answer_strategy(query)
    strategy = strategy_info["strategy"]


    # order_id_fact_priority_gate:
    # 结构化订单号是强事实信号。只要用户明确提供订单号，
    # 且不是风险升级/寒暄，就优先进入 FACT_REQUIRED。
    # 这里不是业务关键词分类，而是基于订单号这一结构化事实入口。
    try:
        from app.pipeline import extract_order_id
        _trace_order_id = extract_order_id(query)
    except Exception:
        _trace_order_id = None

    if _trace_order_id and strategy not in {"RISK_HANDOFF", "SMALL_TALK"}:
        strategy = "FACT_REQUIRED"
        strategy_info["strategy"] = strategy
        strategy_info["reason"] = "order_id_fact_priority_gate"
    # Product entity override:
    # 如果商品中心可以召回明确商品实体，而 LLM-only strategy 把它误判成寒暄/低信息/常识，
    # 则提升为 PRODUCT_KNOWLEDGE。这里依据商品实体召回，不维护用户意图关键词。
    if strategy in {"SMALL_TALK", "LOW_INFO", "COMMON_SENSE"}:
        try:
            from app.product_fact_provider import find_product_fact
            if find_product_fact(query):
                strategy = "PRODUCT_KNOWLEDGE"
                strategy_info["strategy"] = strategy
                strategy_info["reason"] = "product_fact_entity_override"
        except Exception:
            pass


    result: Dict[str, Any] = {
        "query": query,
        "strategy": strategy,
        "strategy_reason": strategy_info.get("reason"),
        "need_mainline": strategy_info.get("need_mainline"),
        "mainline_used": False,
        "scene": None,
        "policy_file": None,
        "reply": None,
        "raw_mainline": None,
    }

    def _return_with_context_fallback(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Early-exit branch finalizer.

        如果当前 strategy 是 LOW_INFO / COMMON_SENSE / SMALL_TALK / PRODUCT_KNOWLEDGE，
        且 memory 里有可用历史，则用 context-aware fallback v2 替换原早退回复。
        """
        original_reply = result.get("reply") or ""

        context_fallback = maybe_apply_context_aware_fallback(
            query=query,
            strategy=strategy,
            original_reply=original_reply,
            user_id=user_id,
            product_id=product_id,
        )

        if context_fallback is not None:
            result.update(context_fallback)
            result["query"] = query
            result["strategy"] = strategy
            result["strategy_reason"] = strategy_info.get("reason")
            result["need_mainline"] = strategy_info.get("need_mainline")
            return result

        return result

    if strategy == "LOW_INFO":
        result["reply"] = _reply_low_info(query)
        return _return_with_context_fallback(result)

    if strategy == "SMALL_TALK":
        result["reply"] = _reply_small_talk(query)
        return _return_with_context_fallback(result)

    if strategy == "RISK_HANDOFF":
        result["reply"] = _reply_risk_handoff(query)
        return result

    if strategy in {"PRODUCT_KNOWLEDGE", "COMMON_SENSE"}:
        # 先尝试 context-aware fallback，避免已有历史时还额外调用 LLM 生成原始兜底回复。
        context_fallback = maybe_apply_context_aware_fallback(
            query=query,
            strategy=strategy,
            original_reply="",
            user_id=user_id,
            product_id=product_id,
        )
        if context_fallback is not None:
            result.update(context_fallback)
            result["query"] = query
            result["strategy"] = strategy
            result["strategy_reason"] = strategy_info.get("reason")
            result["need_mainline"] = strategy_info.get("need_mainline")
            return result

        result["reply"] = _reply_product_or_common(query, strategy)
        return result

    from app.pipeline_llm import answer_with_llm

    mainline = answer_with_llm(query, user_id=user_id, product_id=product_id)
    result["mainline_used"] = True

    result["raw_mainline"] = mainline
    # trace_order_id_fallback:
    # answer_with_strategy 作为最终入口时，透传主线或结构抽取得到的订单号。
    # 只补 trace 字段，不改变路由、回复和事实查询逻辑。
    if isinstance(mainline, dict):
        result["order_id"] = mainline.get("order_id") or result.get("order_id")

    if not result.get("order_id"):
        try:
            from app.pipeline import extract_order_id
            result["order_id"] = extract_order_id(query)
        except Exception:
            pass


    if isinstance(mainline, dict):
        result["scene"] = mainline.get("scene")
        result["policy_file"] = mainline.get("policy_file")
        result["reply"] = mainline.get("reply")
    else:
        result["reply"] = str(mainline)

    return result


if __name__ == "__main__":
    samples = [
        "退款多久到账？",
        "我这个订单怎么还没发货？",
        "这个芒果干怎么保存？",
        "在吗",
        "谢谢",
        "你们骗人，我要投诉",
    ]

    for q in samples:
        print("=" * 80)
        r = answer_with_strategy(q)
        print(json.dumps({
            "query": r["query"],
            "strategy": r["strategy"],
            "mainline_used": r["mainline_used"],
            "scene": r["scene"],
            "policy_file": r["policy_file"],
            "reply": r["reply"],
        }, ensure_ascii=False, indent=2))
