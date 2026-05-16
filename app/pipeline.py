from __future__ import annotations
import json
from pathlib import Path
import re
from rag.simple_retriever import retrieve_policy
from tools.order_tool import query_order
from tools.logistics_tool import query_logistics
from tools.refund_tool import query_refund
from tools.aftersale_tool import query_after_sale


def extract_order_id(text: str):
    """
    订单号结构抽取。

    支持：
    - 真实/历史样例中的长数字订单号；
    - Phase20 mock sandbox 中的 ORD1001 这类订单号。
    """
    text = text or ""

    patterns = [
        r"\bORD\d{3,}\b",
        r"\b[A-Z]{2,}\d{3,}\b",
        r"\b\d{10,}\b",
    ]

    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return m.group(0).upper()

    return None

def _load_mock_jsonl(file_name: str):
    root = Path(__file__).resolve().parents[1]
    path = root / "data" / "mock_business" / file_name

    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass

    return rows


def _first_by_order_id(file_name: str, order_id: str):
    if not order_id:
        return None

    target = str(order_id).upper()

    for row in _load_mock_jsonl(file_name):
        if str(row.get("order_id", "")).upper() == target:
            return row

    return None



def _adapt_mock_context_for_mainline(context: dict):
    """
    将 Phase20 mock business schema 适配为主线旧 schema。

    目的：
    - 不改 rule_based_answer；
    - 不改 answer_with_llm；
    - 不新增关键词；
    - 只在事实层补齐主线依赖的稳定字段。
    """
    order = context.get("order")
    product = context.get("product")
    inventory = context.get("inventory")
    refund = context.get("refund")
    logistics = context.get("logistics")

    if order:
        if product:
            order.setdefault("product_name", product.get("title") or product.get("name") or product.get("product_name"))
        else:
            order.setdefault("product_name", order.get("product_id") or "商品")

        order.setdefault("sku", order.get("sku_id") or order.get("sku_name") or "")

        if inventory:
            stock_qty = inventory.get("stock_qty")
            if stock_qty is not None:
                order.setdefault("stock_status", "有库存" if int(stock_qty) > 0 else "无库存")
            else:
                order.setdefault("stock_status", "库存状态以系统查询为准")
        else:
            order.setdefault("stock_status", "库存状态以系统查询为准")

        # 旧主线常用字段：promise_ship_hours。
        # mock 中更准确的是 promise_ship_before，这里只补兼容值，同时保留原字段。
        order.setdefault("promise_ship_hours", 48)

        # 旧主线价保/金额字段兼容。
        if "order_amount" not in order and "paid_amount" in order:
            order["order_amount"] = order["paid_amount"]
        order.setdefault("current_price", order.get("paid_amount"))

        # 旧主线可能展示下单/付款时间。
        if "created_time" not in order and "created_at" in order:
            order["created_time"] = order["created_at"]

        if "pay_time" not in order:
            order["pay_time"] = (
                order.get("paid_at")
                or order.get("pay_at")
                or order.get("created_at")
                or order.get("created_time")
                or ""
            )

        # 旧主线字段兜底，避免 mock schema 缺字段导致主链路中断。
        order.setdefault("order_status", order.get("status") or "订单状态以系统查询为准")
        order.setdefault("shipping_status", order.get("shipping_status") or "发货状态以系统查询为准")
        order.setdefault("refund_status", order.get("refund_status") or "none")
        order.setdefault("address_region", order.get("address_region") or "")
        order.setdefault("can_modify_address", bool(order.get("can_modify_address", False)))

    if logistics:
        logistics.setdefault("logistics_status", logistics.get("status") or logistics.get("shipping_status") or "物流状态以系统查询为准")
        logistics.setdefault("latest_node", logistics.get("latest_node") or logistics.get("last_node") or logistics.get("current_node") or "")
        logistics.setdefault("latest_time", logistics.get("latest_time") or logistics.get("updated_at") or "")
        logistics.setdefault("signed_by", logistics.get("signed_by"))

    if refund:
        refund.setdefault("refund_status", refund.get("status") or "退款状态以系统查询为准")
        refund.setdefault("refund_amount", refund.get("amount") or refund.get("refund_amount") or 0)
        refund.setdefault("apply_time", refund.get("apply_time") or refund.get("created_at") or "")
        refund.setdefault("expected_arrival", refund.get("expected_arrival") or "以支付渠道实际到账时间为准")
        refund.setdefault("pay_channel", refund.get("pay_channel") or refund.get("channel") or "原支付渠道")

    return context


def _mock_business_context(order_id: str | None):
    """
    Phase20 mock business fact fallback。

    作用：
    - 不替代真实数据库；
    - 只在原业务查询无结果时补充 demo / eval 所需事实；
    - 让主线可以展示 tool-use / fact grounding 闭环。
    """
    if not order_id:
        return {
            "order": None,
            "logistics": None,
            "refund": None,
            "after_sale": None,
            "fact_source": "missing_order_id",
        }

    order = _first_by_order_id("orders.jsonl", order_id)
    logistics = _first_by_order_id("logistics.jsonl", order_id)
    refund = _first_by_order_id("refunds.jsonl", order_id)

    after_sale = (
        _first_by_order_id("after_sales.jsonl", order_id)
        or _first_by_order_id("after_sale.jsonl", order_id)
    )

    product = None
    inventory = None
    promotion = None

    product_id = None
    if order:
        product_id = order.get("product_id") or order.get("item_id")

    if product_id:
        for row in _load_mock_jsonl("products.jsonl"):
            if str(row.get("product_id", "")) == str(product_id) or str(row.get("item_id", "")) == str(product_id):
                product = row
                break

        for row in _load_mock_jsonl("inventory.jsonl"):
            if str(row.get("product_id", "")) == str(product_id) or str(row.get("item_id", "")) == str(product_id):
                inventory = row
                break

        for row in _load_mock_jsonl("promotions.jsonl"):
            if str(row.get("product_id", "")) == str(product_id) or str(row.get("item_id", "")) == str(product_id):
                promotion = row
                break

    context = {
        "order": order,
        "logistics": logistics,
        "refund": refund,
        "after_sale": after_sale,
        "product": product,
        "inventory": inventory,
        "promotion": promotion,
        "fact_source": "mock_business_jsonl",
    }

    return _adapt_mock_context_for_mainline(context)


def build_business_context(order_id: str | None):
    """
    构建业务事实上下文。

    优先使用原有工具/数据库；
    如果没有查到任何订单事实，则 fallback 到 Phase20 mock business sandbox。
    """
    if not order_id:
        return {
            "order": None,
            "logistics": None,
            "refund": None,
            "after_sale": None,
            "fact_source": "missing_order_id",
        }

    context = {
        "order": query_order(order_id),
        "logistics": query_logistics(order_id),
        "refund": query_refund(order_id),
        "after_sale": query_after_sale(order_id),
        "fact_source": "primary_tools",
    }

    if any(context.get(k) for k in ["order", "logistics", "refund", "after_sale"]):
        return context

    return _mock_business_context(order_id)
def rule_based_answer(user_query: str, policy: dict, context: dict):
    # Fact-first guard: structured business facts should override generic SOP replies.
    # This is based on order/refund/logistics facts, not user-expression keyword routing.
    _scene = policy.get("scene") if isinstance(policy, dict) else None
    _order = context.get("order") if context else None
    _logistics = context.get("logistics") if context else None
    _refund = context.get("refund") if context else None

    # express_policy_factless_guard:
    # 已经进入快递方式/到付场景时，如果没有订单事实，给稳定客服口径，避免泛化跑偏。
    if _scene == "express_policy" and not _order:
        return (
            "您好，快递方式需要以商品页面、下单页可选项和商家实际发货安排为准。"
            "如果您想指定顺丰或到付，建议先把收货地区发我，我帮您确认是否支持；"
            "未确认前我不能直接承诺一定可以顺丰到付。"
        )

    if _scene == "shipping_policy" and _order:
        _shipping_status = _order.get("shipping_status")
        _order_status = _order.get("order_status")
        if _shipping_status == "not_shipped" or _order_status == "paid_pending_ship":
            _promise_before = _order.get("promise_ship_before")
            _promise_hours = _order.get("promise_ship_hours")
            _promise_text = (
                f"承诺最晚发货时间为 {_promise_before}"
                if _promise_before
                else f"承诺发货时效为付款后 {_promise_hours} 小时内"
            )
            return (
                f"抱歉让您久等了，我帮您查到订单 {_order.get('order_id')} 当前是【待发货】状态。\n"
                f"商品为「{_order.get('product_name')} {_order.get('sku', '')}」，"
                f"库存状态是【{_order.get('stock_status', '以系统查询为准')}】，{_promise_text}。\n"
                f"我可以先帮您反馈催发货/申请加急；如果超过承诺时间仍未发出，建议您再联系人工继续核实。"
            )

    if _scene == "logistics_policy" and _order and not _logistics:
        _shipping_status = _order.get("shipping_status")
        if _shipping_status == "not_shipped" or _order.get("order_status") == "paid_pending_ship":
            _promise_before = _order.get("promise_ship_before")
            _promise_text = f"，承诺最晚发货时间为 {_promise_before}" if _promise_before else ""
            return (
                f"我帮您查到订单 {_order.get('order_id')} 目前还没有发货，所以暂时不会产生物流轨迹。\n"
                f"当前订单状态是【待发货】{_promise_text}。\n"
                f"您可以先等待商家发货；如果超过承诺时间仍未发出，我可以帮您反馈催发货或转人工继续核实。"
            )

    if _scene == "refund_policy" and _order and not _refund:
        _refund_status = _order.get("refund_status")
        if _refund_status in {None, "", "none", "NONE", "无", "未申请"}:
            return (
                f"我帮您查到订单 {_order.get('order_id')} 当前没有查询到退款申请或退款处理中记录。\n"
                f"如果您已经提交过退款申请，建议您再确认一下订单详情页的售后/退款进度；"
                f"如果还没有提交，需要先在订单详情页发起退款或售后申请。\n"
                f"退款到账时间需要以实际退款申请状态和原支付渠道处理时间为准，我这边不能直接承诺固定到账时间。"
            )
    scene = policy["scene"]
    order = context.get("order")
    logistics = context.get("logistics")
    refund = context.get("refund")
    after_sale = context.get("after_sale")

    if scene == "price_protection":
        if order:
            if order["current_price"] < order["order_amount"]:
                diff = order["order_amount"] - order["current_price"]
                return (
                    f"理解您的心情，刚买就降价确实会让人不舒服。\n"
                    f"我帮您查到订单 {order['order_id']} 的下单金额是 {order['order_amount']} 元，当前参考价格是 {order['current_price']} 元，差额约 {diff:.2f} 元。\n"
                    f"这个情况建议优先申请价保，您可以在【订单详情 → 申请价保】提交差价补偿申请。\n"
                    f"最终是否通过需要以平台价保规则和页面审核结果为准，我也可以继续帮您核实。"
                )
            return (
                f"我帮您查到订单 {order['order_id']} 当前价格暂未低于下单金额。\n"
                f"如果您看到商品页面有更低价格，可以截图发来，我帮您核实是否符合价保条件。\n"
                f"一般可在【订单详情 → 申请价保】查看是否支持补差价。"
            )
        return (
            "理解您的心情，刚买就降价确实会让人不舒服。我先帮您看看是否支持价保。\n"
            "一般在价保期内，如果商品页面价格下调，可以在【订单详情 → 申请价保】提交差价补偿。\n"
            "麻烦您提供订单号和当前商品页面截图，我帮您核实是否符合价保条件。"
        )

    if scene == "shipping_policy":
        if order:
            return (
                f"抱歉让您久等了，我帮您查到订单 {order['order_id']} 当前状态是【{order['order_status']}】。\n"
                f"商品为「{order['product_name']} {order['sku']}」，库存状态是【{order['stock_status']}】，承诺发货时效为付款后 {order['promise_ship_hours']} 小时内。\n"
                f"我可以帮您催促仓库尽快处理；如果已经超过承诺发货时间，也可以进一步反馈加急。"
            )
        return (
            "抱歉让您久等了，我帮您看一下发货进度。\n"
            "麻烦您发一下订单号，我会确认是否已分配库存、是否等待打包或是否存在调拨情况。\n"
            "如果确实超时，我也会帮您同步申请加急处理。"
        )

    if scene == "logistics_policy":
        if logistics:
            return (
                f"我帮您查到物流状态是【{logistics['logistics_status']}】，最新节点为：{logistics['latest_node']}，更新时间：{logistics['latest_time']}。\n"
                f"如果页面显示签收但您未收到，我会建议先核实签收人、快递柜/驿站和派送网点记录。\n"
                f"若确认物流异常，我们会协助联系快递并按平台规则处理。"
            )

        if "驿站" in user_query or "代收" in user_query or "取件" in user_query:
            return (
                "抱歉让您担心了，我先帮您按驿站代收异常来处理。\n"
                "建议您先核实驿站取件码、代收点记录和快递员派送记录，避免是系统已签收但驿站暂未上架或取件码未同步。\n"
                "麻烦您提供订单号或快递单号，我会继续帮您查询包裹当前节点、签收记录和派送网点；如果确认异常，我们会协助联系快递处理。"
            )

        return (
            "抱歉让您担心了，我先帮您核实物流情况。\n"
            "麻烦您提供订单号或快递单号，我会查询包裹当前节点、签收记录和派送网点。\n"
            "如果确认异常，我们会协助联系快递处理。"
        )

    if scene == "refund_policy":
        if refund:
            return (
                f"我帮您查到这笔退款当前状态是【{refund['refund_status']}】，退款金额 {refund['refund_amount']} 元，支付方式为 {refund['pay_channel']}。\n"
                f"预计到账时间为：{refund['expected_arrival']}。\n"
                f"退款通常会按原支付路径退回，您也可以在【订单详情 → 退款进度】查看最新状态。"
            )
        return (
            "退款一般会按原支付路径退回，到账时间和支付方式有关。\n"
            "您可以在【订单详情 → 退款进度】查看当前状态。\n"
            "麻烦您提供订单号，我帮您确认目前是商家处理中、平台处理中，还是支付渠道到账中。"
        )

    if scene == "quality_issue":
        if after_sale:
            return (
                f"抱歉给您带来不好的体验，我帮您查到该订单售后状态是【{after_sale['after_sale_status']}】，问题类型为【{after_sale['issue_type']}】。\n"
                f"当前需要补充的凭证包括：{after_sale['evidence_required']}。\n"
                f"核实后可处理方案包括：{after_sale['solution_options']}。您可以在【订单详情 → 申请售后】继续上传材料。"
            )
        return (
            "抱歉给您带来不好的体验，质量问题我们会协助处理。\n"
            "您可以在【订单详情 → 申请售后】选择退货、换货或维修，并上传问题照片/视频。\n"
            "麻烦您把订单号和问题图片发我，我帮您优先核实处理。"
        )

    if scene == "complaint_policy":
        return (
            "非常抱歉让您有这样的体验，我能理解您现在比较着急。\n"
            "我会先帮您把问题梳理清楚并跟进处理，不会让您来回重复说明。\n"
            "麻烦您把订单号和具体问题发我，我会优先核实当前进度，并尽快给您一个明确处理方向。"
        )

    return (
        "可以帮您看一下哈。若商品支持 7 天无理由，并且吊牌、包装完整，没有清洗、污渍、异味或影响二次销售，一般可以申请退货或换货。\n"
        "如果只是室内试穿后发现尺码不合适，可以在【订单详情 → 申请售后】里选择退货退款或换货。\n"
        "如果已经实际穿着外出、清洗过或吊牌缺失，可能无法直接支持无理由退货，建议您发订单号和商品现状照片，我帮您判断。"
    )

def answer(user_query: str):
    order_id = extract_order_id(user_query)
    policy = retrieve_policy(user_query)
    context = build_business_context(order_id)
    reply = rule_based_answer(user_query, policy, context)

    return {
        "order_id": order_id,
        "scene": policy["scene"],
        "policy_file": policy["file_name"],
        "business_context": context,
        "reply": reply,
        "retrieved_policy": policy["content"],
    }
