# -*- coding: utf-8 -*-
"""
Merchant / Product / Activity fact tool v1.

定位：
- 离线/旁路事实工具；
- 不替代平台 SOP；
- 不做线上关键词路由；
- 只从 merchant fact cards 中检索可核实事实；
- fact 不足时返回 need_more_info，避免模型猜测商品/活动/库存信息。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_FACT_PATH = Path("data/merchant_facts/mock_merchant_facts.jsonl")


def _load_facts(path: Path = DEFAULT_FACT_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
            except Exception:
                continue
    return rows


def _text_of_fact(card: Dict[str, Any]) -> str:
    parts = [
        card.get("fact_id", ""),
        card.get("fact_group", ""),
        card.get("scope", ""),
        card.get("product_id", ""),
        card.get("sku_id", ""),
        card.get("title", ""),
        json.dumps(card.get("facts", {}), ensure_ascii=False),
        card.get("customer_reply_guidance", ""),
        " ".join(card.get("do_not_say") or []),
        " ".join(card.get("need_human_conditions") or []),
    ]
    return " ".join(str(x) for x in parts if x)


def _char_overlap_score(query: str, text: str) -> float:
    """
    简单字符覆盖评分。
    注意：这是 fact-card 检索评分，不是线上业务分类词表。
    """
    query = (query or "").strip()
    text = (text or "").strip()

    if not query or not text:
        return 0.0

    q_chars = set(ch for ch in query if not ch.isspace())
    if not q_chars:
        return 0.0

    hit = sum(1 for ch in q_chars if ch in text)
    return hit / max(len(q_chars), 1)


def query_merchant_facts(
    query: str,
    *,
    product_id: Optional[str] = None,
    sku_id: Optional[str] = None,
    fact_group: Optional[str] = None,
    top_k: int = 3,
    min_score: float = 0.08,
    fact_path: Path = DEFAULT_FACT_PATH,
) -> Dict[str, Any]:
    """
    查询 merchant/product/activity facts。

    返回：
    - hit: 是否有可用 fact
    - need_more_info: 是否需要用户补充商品/订单/截图
    - facts: top fact cards
    """
    facts = _load_facts(fact_path)

    scored = []
    for card in facts:
        if fact_group and card.get("fact_group") != fact_group:
            continue

        score = _char_overlap_score(query, _text_of_fact(card))

        if product_id and card.get("product_id") == product_id:
            score += 0.5

        if sku_id and card.get("sku_id") == sku_id:
            score += 0.3

        if score >= min_score:
            cc = dict(card)
            cc["score"] = round(score, 4)
            scored.append(cc)

    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = scored[:top_k]

    return {
        "hit": bool(top),
        "need_more_info": not bool(top),
        "query": query,
        "product_id": product_id,
        "sku_id": sku_id,
        "fact_group": fact_group,
        "facts": top,
        "fact_count": len(top),
    }


def build_merchant_fact_reply(query: str, fact_result: Dict[str, Any]) -> str:
    """
    根据 fact 查询结果生成保守客服回复。
    只用于 smoke / 旁路演示，不直接替代主链路 LLM。
    """
    facts = fact_result.get("facts") or []

    if not facts:
        return (
            "您好，这个问题需要结合具体商品页面、店铺活动配置或订单状态核实。"
            "为了避免说错商品参数、赠品、优惠、库存或配送信息，"
            "麻烦您发一下商品链接、订单号或页面截图，我再帮您确认。"
        )

    top = facts[0]
    guidance = top.get("customer_reply_guidance") or ""

    if guidance:
        return guidance

    return (
        "您好，这个问题我需要结合商品页面或店铺配置进一步核实。"
        "麻烦您补充商品链接、订单号或页面截图，我再帮您确认。"
    )


if __name__ == "__main__":
    tests = [
        "这个是纯棉的吗，会不会有荧光增白剂？",
        "买二送一那买四送二吗？",
        "满39送花茶，给个链接",
        "能指定发邮政吗？",
        "可以开发票吗？",
        "我要买很多，有批发价吗？",
    ]

    for q in tests:
        r = query_merchant_facts(q)
        print("=" * 100)
        print("query:", q)
        print("hit:", r["hit"])
        print("top:", [(x.get("fact_id"), x.get("fact_group"), x.get("score")) for x in r["facts"]])
        print("reply:", build_merchant_fact_reply(q, r))
