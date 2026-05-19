# -*- coding: utf-8 -*-
"""
Merchant fact shadow side context.

只做旁路观察：
- 不改变主链路 reply
- 不改变 strategy
- 不替代 SOP/RAG
- 只把 merchant fact 命中情况写入 result/debug
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


def run_merchant_fact_shadow(
    query: str,
    *,
    product_id: Optional[str] = None,
    sku_id: Optional[str] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    if os.getenv("USE_MERCHANT_FACT_LAYER", "0") != "1":
        return {
            "enabled": False,
            "reason": "USE_MERCHANT_FACT_LAYER_off",
        }

    if os.getenv("USE_MERCHANT_FACT_SHADOW", "0") != "1":
        return {
            "enabled": False,
            "reason": "USE_MERCHANT_FACT_SHADOW_off",
        }

    try:
        from tools.merchant_fact_tool import (
            query_merchant_facts,
            build_merchant_fact_reply,
        )

        fact_result = query_merchant_facts(
            query,
            product_id=product_id,
            sku_id=sku_id,
            top_k=top_k,
        )

        side_reply = build_merchant_fact_reply(query, fact_result)

        facts = fact_result.get("facts") or []
        top_fact = facts[0] if facts else {}

        return {
            "enabled": True,
            "hit": bool(facts),
            "need_more_info": fact_result.get("need_more_info"),
            "fact_count": fact_result.get("fact_count"),
            "top_fact_id": top_fact.get("fact_id"),
            "top_fact_group": top_fact.get("fact_group"),
            "top_fact_score": top_fact.get("score"),
            "top_facts": [
                {
                    "fact_id": x.get("fact_id"),
                    "fact_group": x.get("fact_group"),
                    "title": x.get("title"),
                    "score": x.get("score"),
                }
                for x in facts
            ],
            "side_reply_preview": side_reply,
            "note": "shadow_only_not_used_as_final_reply",
        }

    except Exception as e:
        return {
            "enabled": True,
            "hit": False,
            "error": str(e),
        }
