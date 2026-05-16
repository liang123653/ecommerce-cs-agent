# -*- coding: utf-8 -*-
"""
Product fact provider for mainline answer strategy.

这个模块不是关键词路由器。
它只做一件事：从商品中心 mock jsonl 中找和用户 query 相关的商品事实。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


MOCK_DIR = Path(__file__).resolve().parents[1] / "data" / "mock_business"


def _load_jsonl(name: str) -> List[Dict[str, Any]]:
    path = MOCK_DIR / name
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


def _score_product(query: str, product: Dict[str, Any]) -> int:
    """
    简单实体匹配，不做业务意图分类。

    评分依据来自商品中心字段：
    - title
    - category
    - product_id
    """
    q = query or ""
    score = 0

    title = str(product.get("title") or product.get("name") or "")
    category = str(product.get("category") or "")
    product_id = str(product.get("product_id") or "")

    if title and title in q:
        score += 10

    # title 分词不做复杂 NLP，只保留商品名里的连续中文片段做实体召回。
    for token in [title.replace("500g", "").replace("250g", "").strip(), category, product_id]:
        if token and token in q:
            score += 5

    return score


def find_product_fact(query: str) -> Optional[Dict[str, Any]]:
    products = _load_jsonl("products.jsonl")
    if not products:
        return None

    scored = []
    for p in products:
        s = _score_product(query, p)
        if s > 0:
            scored.append((s, p))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    product = dict(scored[0][1])

    product_id = product.get("product_id")
    inventory = None
    promotion = None

    if product_id:
        for row in _load_jsonl("inventory.jsonl"):
            if str(row.get("product_id")) == str(product_id):
                inventory = row
                break

        for row in _load_jsonl("promotions.jsonl"):
            if str(row.get("product_id")) == str(product_id):
                promotion = row
                break

    return {
        "product": product,
        "inventory": inventory,
        "promotion": promotion,
        "fact_source": "mock_product_center",
    }


def build_product_fact_summary(fact: Optional[Dict[str, Any]]) -> str:
    if not fact:
        return ""

    product = fact.get("product") or {}
    inventory = fact.get("inventory") or {}
    promotion = fact.get("promotion") or {}

    lines = []

    if product:
        lines.append(f"商品名称：{product.get('title') or product.get('name') or ''}")
        if product.get("category"):
            lines.append(f"商品类目：{product.get('category')}")
        if product.get("shelf_life"):
            lines.append(f"保质期：{product.get('shelf_life')}")
        if product.get("storage"):
            lines.append(f"保存方式：{product.get('storage')}")
        if product.get("eating_method"):
            lines.append(f"食用方式：{product.get('eating_method')}")
        if product.get("quality_note"):
            lines.append(f"售后提示：{product.get('quality_note')}")

    if inventory:
        if inventory.get("stock_qty") is not None:
            lines.append(f"库存数量：{inventory.get('stock_qty')}")
        if inventory.get("can_ship_today") is not None:
            lines.append(f"是否可当天发货：{inventory.get('can_ship_today')}")

    if promotion:
        if promotion.get("summary"):
            lines.append(f"活动信息：{promotion.get('summary')}")

    return "\n".join(f"- {x}" for x in lines if x)


def build_product_fact_context(fact: Optional[Dict[str, Any]]) -> str:
    """
    给 LLM 使用的商品事实上下文。
    这是内部上下文，不直接原样展示给用户。
    """
    if not fact:
        return ""

    product = fact.get("product") or {}
    inventory = fact.get("inventory") or {}
    promotion = fact.get("promotion") or {}

    lines = []

    if product:
        for key, label in [
            ("title", "商品名称"),
            ("category", "商品类目"),
            ("shelf_life", "保质期"),
            ("storage", "保存方式"),
            ("eating_method", "食用方式"),
            ("quality_note", "售后提示"),
        ]:
            value = product.get(key)
            if value:
                lines.append(f"{label}: {value}")

    if inventory:
        stock_qty = inventory.get("stock_qty")
        if stock_qty is not None:
            lines.append(f"库存数量: {stock_qty}")

        can_ship_today = inventory.get("can_ship_today")
        if can_ship_today is True:
            lines.append("当天发货能力: 当前商品中心显示可当天发货")
        elif can_ship_today is False:
            lines.append("当天发货能力: 当前商品中心显示不可当天发货")

    if promotion and promotion.get("summary"):
        lines.append(f"活动信息: {promotion.get('summary')}")

    return "\n".join(lines)
