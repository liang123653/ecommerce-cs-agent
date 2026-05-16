from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MOCK_DATA = Path("data/mock_business_facts/fact_query_mock_data.json")


def _load_data(data_path: str | Path = DEFAULT_MOCK_DATA) -> Dict[str, Any]:
    path = Path(data_path)
    if not path.exists():
        return {
            "stores": {},
            "orders": {},
            "logistics": {},
            "after_sales": {},
            "return_shipping": {},
            "products": {},
            "promotions": {},
            "memories": [],
        }

    return json.loads(path.read_text(encoding="utf-8"))


def _get_order(data: Dict[str, Any], order_id: str) -> Dict[str, Any]:
    return data.get("orders", {}).get(str(order_id), {}) or {}


def _get_store(data: Dict[str, Any], store_id: str) -> Dict[str, Any]:
    return data.get("stores", {}).get(str(store_id), {}) or {}


def _get_product(data: Dict[str, Any], product_id: str) -> Dict[str, Any]:
    return data.get("products", {}).get(str(product_id), {}) or {}


def shipping_fact_query(
    order_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    发货前履约事实查询。

    用于：
    - 什么时候发货
    - 今天能不能发
    - 还没发货
    - 是否超过承诺发货时间
    """
    data = _load_data(data_path)
    order = _get_order(data, order_id)

    return {
        "found": bool(order),
        "order_id": str(order_id),
        "paid_time": order.get("paid_time"),
        "promised_ship_deadline": order.get("promised_ship_deadline"),
        "current_fulfillment_status": order.get("current_fulfillment_status", "unknown"),
        "has_shipped": bool(order.get("has_shipped", False)),
        "warehouse_status": order.get("warehouse_status"),
        "is_presale": bool(order.get("is_presale", False)),
        "is_customized": bool(order.get("is_customized", False)),
        "is_overdue": bool(order.get("is_overdue", False)),
        "seller_note": order.get("seller_note"),
    }


def logistics_fact_query(
    order_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    发货后物流事实查询。

    用于：
    - 物流不更新
    - 快递未收到
    - 轨迹异常
    - 疑似虚假发货
    """
    data = _load_data(data_path)
    logistics = data.get("logistics", {}).get(str(order_id), {}) or {}

    return {
        "found": bool(logistics),
        "order_id": str(order_id),
        "tracking_no": logistics.get("tracking_no"),
        "carrier": logistics.get("carrier"),
        "shipped_time": logistics.get("shipped_time"),
        "latest_tracking_status": logistics.get("latest_tracking_status"),
        "latest_tracking_time": logistics.get("latest_tracking_time"),
        "is_tracking_stalled": bool(logistics.get("is_tracking_stalled", False)),
        "is_returned": bool(logistics.get("is_returned", False)),
        "is_delivered": bool(logistics.get("is_delivered", False)),
        "has_abnormal_tracking": bool(logistics.get("has_abnormal_tracking", False)),
    }


def express_policy_fact_query(
    store_id: str,
    address_region: Optional[str] = None,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    快递偏好与快递可用性查询。
    """
    data = _load_data(data_path)
    store = _get_store(data, store_id)

    return {
        "found": bool(store),
        "store_id": str(store_id),
        "address_region": address_region,
        "default_carriers": store.get("default_carriers", []),
        "supported_carriers": store.get("supported_carriers", []),
        "unsupported_carriers": store.get("unsupported_carriers", []),
        "can_note_preference": bool(store.get("can_note_preference", False)),
        "can_guarantee_specific_carrier": bool(store.get("can_guarantee_specific_carrier", False)),
        "warehouse_constraints": store.get("warehouse_constraints"),
    }


def return_refund_fact_query(
    order_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    退货、退款、退货地址和退款到账事实查询。
    """
    data = _load_data(data_path)
    order = _get_order(data, order_id)
    after_sale = data.get("after_sales", {}).get(str(order_id), {}) or {}

    return {
        "found": bool(order) or bool(after_sale),
        "order_id": str(order_id),
        "order_status": order.get("order_status", "unknown"),
        "signed_time": order.get("signed_time"),
        "supports_7day_return": after_sale.get(
            "supports_7day_return",
            _get_product(data, order.get("product_id", "")).get("supports_7day_return"),
        ),
        "package_opened": after_sale.get("package_opened"),
        "affects_resale": after_sale.get("affects_resale"),
        "return_application_status": after_sale.get("return_application_status"),
        "refund_application_status": after_sale.get("refund_application_status"),
        "refund_amount": after_sale.get("refund_amount"),
        "refund_channel": after_sale.get("refund_channel"),
        "refund_arrival_status": after_sale.get("refund_arrival_status"),
        "return_address_available": bool(after_sale.get("return_address_available", False)),
        "return_tracking_status": after_sale.get("return_tracking_status"),
    }


def after_sale_fact_query(
    order_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    售后申请、商家处理、平台介入状态查询。
    """
    data = _load_data(data_path)
    after_sale = data.get("after_sales", {}).get(str(order_id), {}) or {}

    return {
        "found": bool(after_sale),
        "order_id": str(order_id),
        "after_sale_type": after_sale.get("after_sale_type"),
        "after_sale_status": after_sale.get("after_sale_status"),
        "seller_response_status": after_sale.get("seller_response_status"),
        "evidence_uploaded": bool(after_sale.get("evidence_uploaded", False)),
        "platform_intervention_status": after_sale.get("platform_intervention_status"),
        "risk_need_human": bool(after_sale.get("risk_need_human", False)),
    }


def return_shipping_fact_query(
    order_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    退货运费、退货宝、运费险、运费补偿事实查询。
    """
    data = _load_data(data_path)
    item = data.get("return_shipping", {}).get(str(order_id), {}) or {}

    return {
        "found": bool(item),
        "order_id": str(order_id),
        "has_return_shipping_protection": item.get("has_return_shipping_protection"),
        "return_shipping_method": item.get("return_shipping_method"),
        "return_shipping_fee": item.get("return_shipping_fee"),
        "compensation_status": item.get("compensation_status"),
        "compensation_amount": item.get("compensation_amount"),
        "compensation_arrival_status": item.get("compensation_arrival_status"),
    }


def promotion_fact_query(
    store_id: str,
    product_id: Optional[str] = None,
    user_id: Optional[str] = None,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    活动、优惠券、改价、老客价等配置查询。
    """
    data = _load_data(data_path)
    promo = data.get("promotions", {}).get(str(store_id), {}) or {}

    return {
        "found": bool(promo),
        "store_id": str(store_id),
        "product_id": product_id,
        "user_id": user_id,
        "active_promotions": promo.get("active_promotions", []),
        "available_coupons": promo.get("available_coupons", []),
        "can_modify_price": bool(promo.get("can_modify_price", False)),
        "member_price_policy": promo.get("member_price_policy"),
        "manual_discount_allowed": bool(promo.get("manual_discount_allowed", False)),
    }


def product_fact_query(
    product_id: str,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    商品属性、规格、库存、页面说明查询。
    """
    data = _load_data(data_path)
    product = _get_product(data, product_id)

    return {
        "found": bool(product),
        "product_id": str(product_id),
        "title": product.get("title"),
        "attributes": product.get("attributes", {}),
        "stock_status": product.get("stock_status"),
        "description_summary": product.get("description_summary"),
        "supports_7day_return": product.get("supports_7day_return"),
        "gift_policy": product.get("gift_policy"),
    }


def memory_fact_query(
    user_id: str,
    order_id: Optional[str] = None,
    product_id: Optional[str] = None,
    data_path: str | Path = DEFAULT_MOCK_DATA,
) -> Dict[str, Any]:
    """
    历史对话承诺查询。

    用于识别售前承诺与商品事实冲突。
    """
    data = _load_data(data_path)
    memories: List[Dict[str, Any]] = data.get("memories", [])

    matched = []
    for m in memories:
        if str(m.get("user_id")) != str(user_id):
            continue
        if order_id is not None and str(m.get("order_id")) != str(order_id):
            continue
        if product_id is not None and str(m.get("product_id")) != str(product_id):
            continue
        matched.append(m)

    has_pre_sale_commitment = any(
        m.get("memory_type") == "pre_sale_commitment" for m in matched
    )

    commitment_summary = None
    conflict = False

    for m in matched:
        if m.get("commitment_summary") and commitment_summary is None:
            commitment_summary = m.get("commitment_summary")
        if m.get("conflict_with_product_fact"):
            conflict = True

    return {
        "found": bool(matched),
        "user_id": str(user_id),
        "order_id": order_id,
        "product_id": product_id,
        "memory_evidence": matched,
        "has_pre_sale_commitment": has_pre_sale_commitment,
        "commitment_summary": commitment_summary,
        "conflict_with_product_fact": conflict,
    }


if __name__ == "__main__":
    print(json.dumps(shipping_fact_query("202604240001"), ensure_ascii=False, indent=2))
