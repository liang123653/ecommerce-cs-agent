# -*- coding: utf-8 -*-
"""
Mock business fact tools for Phase20.

这些工具只读取 data/mock_business 下的 mock JSONL。
不要把它表述为真实业务库。
"""

import json
from pathlib import Path


DATA_DIR = Path("data/mock_business")


def _read_jsonl(name):
    path = DATA_DIR / name
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _index(rows, key):
    return {r.get(key): r for r in rows if r.get(key) is not None}


def _all():
    stores = _read_jsonl("stores.jsonl")
    products = _read_jsonl("products.jsonl")
    inventory = _read_jsonl("inventory.jsonl")
    promotions = _read_jsonl("promotions.jsonl")
    orders = _read_jsonl("orders.jsonl")
    logistics = _read_jsonl("logistics.jsonl")
    refunds = _read_jsonl("refunds.jsonl")

    return {
        "stores": stores,
        "products": products,
        "inventory": inventory,
        "promotions": promotions,
        "orders": orders,
        "logistics": logistics,
        "refunds": refunds,
        "store_by_id": _index(stores, "store_id"),
        "product_by_id": _index(products, "product_id"),
        "order_by_id": _index(orders, "order_id"),
        "logistics_by_order": _index(logistics, "order_id"),
        "refund_by_order": _index(refunds, "order_id"),
    }


def query_order(order_id):
    if not order_id:
        return {"ok": False, "missing_required_args": ["order_id"], "fact": None}

    data = _all()
    fact = data["order_by_id"].get(order_id)
    if not fact:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "order_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": fact}


def query_store(store_id):
    if not store_id:
        return {"ok": False, "missing_required_args": ["store_id"], "fact": None}

    data = _all()
    fact = data["store_by_id"].get(store_id)
    if not fact:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "store_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": fact}


def query_product(product_id):
    if not product_id:
        return {"ok": False, "missing_required_args": ["product_id"], "fact": None}

    data = _all()
    fact = data["product_by_id"].get(product_id)
    if not fact:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "product_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": fact}


def query_inventory(product_id, store_id=None):
    if not product_id:
        return {"ok": False, "missing_required_args": ["product_id"], "fact": None}

    data = _all()
    rows = [
        r for r in data["inventory"]
        if r.get("product_id") == product_id and (not store_id or r.get("store_id") == store_id)
    ]

    if not rows:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "inventory_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": rows[0]}


def query_promotion(store_id=None, product_id=None):
    missing = []
    if not store_id:
        missing.append("store_id")

    if missing:
        return {"ok": False, "missing_required_args": missing, "fact": None}

    data = _all()
    rows = [
        r for r in data["promotions"]
        if r.get("store_id") == store_id and (not product_id or r.get("product_id") == product_id)
    ]

    if not rows:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "promotion_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": rows[0]}


def query_logistics(order_id=None, tracking_no=None):
    if not order_id and not tracking_no:
        return {"ok": False, "missing_required_args": ["order_id"], "fact": None}

    data = _all()

    fact = None
    if order_id:
        fact = data["logistics_by_order"].get(order_id)
    else:
        for r in data["logistics"]:
            if r.get("tracking_no") == tracking_no:
                fact = r
                break

    if not fact:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "logistics_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": fact}


def query_refund(order_id=None, refund_id=None):
    if not order_id and not refund_id:
        return {"ok": False, "missing_required_args": ["order_id"], "fact": None}

    data = _all()

    fact = None
    if order_id:
        fact = data["refund_by_order"].get(order_id)
    else:
        for r in data["refunds"]:
            if r.get("refund_id") == refund_id:
                fact = r
                break

    if not fact:
        return {"ok": False, "missing_required_args": [], "fact": None, "error": "refund_not_found"}

    return {"ok": True, "missing_required_args": [], "fact": fact}
