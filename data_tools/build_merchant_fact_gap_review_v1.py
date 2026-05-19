# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import Counter

SRC = Path("data/eval/real_replay_mining_v1/action_buckets/merchant_fact_gap.jsonl")
OUT = Path("docs/MERCHANT_FACT_GAP_REVIEW_V1.md")


def read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def clean(s, n=120):
    s = "" if s is None else str(s)
    s = s.replace("\n", " ").replace("|", "｜")
    return s[:n]


def get_query(r):
    return (
        r.get("retrieval_query")
        or r.get("query")
        or r.get("last_user_query")
        or ""
    )


rows = read_jsonl(SRC)

scene_counter = Counter((r.get("expected_scene") or "unknown") for r in rows)
source_counter = Counter((r.get("_source_pool") or "unknown") for r in rows)

with OUT.open("w", encoding="utf-8") as f:
    f.write("# Merchant Fact Gap Review v1\n\n")
    f.write(f"- source: `{SRC}`\n")
    f.write(f"- total_rows: {len(rows)}\n\n")

    f.write("## 1. Scene Distribution\n\n")
    f.write("| expected_scene | count |\n|---|---:|\n")
    for k, v in scene_counter.most_common():
        f.write(f"| {k} | {v} |\n")

    f.write("\n## 2. Source Pool Distribution\n\n")
    f.write("| source_pool | count |\n|---|---:|\n")
    for k, v in source_counter.most_common():
        f.write(f"| {k} | {v} |\n")

    f.write("\n## 3. Review Table\n\n")
    f.write("| idx | query | expected_scene | hit_status | top1_scene | top1_score | suggested_fact_group | note |\n")
    f.write("|---:|---|---|---|---|---:|---|---|\n")

    for i, r in enumerate(rows[:200], 1):
        scene = r.get("expected_scene") or ""

        if scene == "product_qa_policy":
            fact_group = "product_fact"
        elif scene == "promotion_policy":
            fact_group = "promotion_fact"
        elif scene == "coupon_policy":
            fact_group = "coupon_fact"
        elif scene == "gift_policy":
            fact_group = "gift_fact"
        elif scene == "stock_policy":
            fact_group = "stock_fact"
        elif scene == "invoice_policy":
            fact_group = "invoice_fact"
        elif scene in {"express_policy", "shipping_fee_policy"}:
            fact_group = "shipping_config_fact"
        elif scene == "order_modify_policy":
            fact_group = "order_modify_fact"
        elif scene == "bulk_purchase_policy":
            fact_group = "bulk_purchase_fact"
        else:
            fact_group = "merchant_fact"

        f.write(
            f"| {i} "
            f"| {clean(get_query(r), 100)} "
            f"| {clean(scene, 40)} "
            f"| {clean(r.get('hit_status'), 30)} "
            f"| {clean(r.get('top1_scene'), 40)} "
            f"| {r.get('top1_score') or 0} "
            f"| {fact_group} "
            f"|  |\n"
        )

print({"out": str(OUT), "rows": len(rows)})
