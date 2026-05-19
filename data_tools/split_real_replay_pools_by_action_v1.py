# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path("data/eval/real_replay_mining_v1")

INPUTS = {
    "no_hit_or_weak": BASE / "no_hit_or_weak_query_sample.jsonl",
    "scene_mismatch": BASE / "scene_mismatch_sample.jsonl",
    "low_score": BASE / "low_score_sample.jsonl",
    "dpo_audit": BASE / "dpo_candidate_audit_sample.jsonl",
}

OUT_DIR = BASE / "action_buckets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = Path("docs/REAL_REPLAY_MINING_V1_DECISION_SUMMARY.md")

# 注意：这是离线分析用的 scene-level action mapping，不是线上路由规则。
MERCHANT_FACT_SCENES = {
    "product_qa_policy",
    "promotion_policy",
    "coupon_policy",
    "gift_policy",
    "stock_policy",
    "bulk_purchase_policy",
    "invoice_policy",
    "express_policy",
    "shipping_fee_policy",
    "order_modify_policy",
}

PLATFORM_SOP_SCENES = {
    "logistics_policy",
    "shipping_policy",
    "refund_policy",
    "return_exchange",
    "quality_issue",
    "description_mismatch",
    "complaint_policy",
    "price_protection",
    "missing_package_policy",
}


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


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def get_query(r):
    return (
        r.get("retrieval_query")
        or r.get("query")
        or r.get("last_user_query")
        or r.get("prompt")
        or ""
    )


def decide_replay_action(r, source_pool):
    scene = r.get("expected_scene") or "unknown"
    top1_scene = r.get("top1_scene") or ""
    hit_status = r.get("hit_status") or ""
    query_info_score = safe_float(r.get("query_info_score"))

    # 弱 query / 低信息优先，不进入 SOP 扩展。
    if hit_status == "weak_query" or (0 < query_info_score < 0.2):
        return "low_info_context_needed"

    # 商品/店铺/活动/库存/赠品/快递配置类，不应先补平台 SOP。
    if scene in MERCHANT_FACT_SCENES:
        return "merchant_fact_gap"

    # unknown 优先看作标签噪声或需要人工判断。
    if scene in {"unknown", ""}:
        return "taxonomy_or_label_gap"

    # 平台 SOP 主干类，进入 SOP/retrieval 诊断。
    if scene in PLATFORM_SOP_SCENES:
        if hit_status == "scene_mismatch" and top1_scene and top1_scene != scene:
            return "retrieval_or_policy_priority_gap"
        return "platform_sop_or_retrieval_gap"

    return "taxonomy_or_label_gap"


def decide_dpo_action(r):
    issues = set(r.get("issues") or [])
    chosen = (r.get("chosen") or "").strip()
    rejected = (r.get("rejected") or "").strip()

    if "same_chosen_rejected" in issues:
        return "dpo_drop_same_pair"

    if "chosen_possible_overpromise" in issues:
        return "dpo_needs_manual_safety_review"

    if "empty_prompt" in issues or "empty_chosen" in issues or "empty_rejected" in issues:
        return "dpo_drop_incomplete"

    if "chosen_too_short" in issues or "rejected_too_short" in issues:
        return "dpo_needs_rewrite_or_drop"

    if len(chosen) >= 30 and len(rejected) >= 30 and chosen != rejected:
        return "dpo_keep_candidate"

    return "dpo_needs_manual_review"


all_bucket_rows = defaultdict(list)
source_stats = {}

for source_name, path in INPUTS.items():
    rows = read_jsonl(path)
    source_stats[source_name] = len(rows)

    for r in rows:
        rr = dict(r)
        rr["_source_pool"] = source_name

        if source_name == "dpo_audit":
            action = decide_dpo_action(rr)
        else:
            action = decide_replay_action(rr, source_name)

        rr["suggested_action_bucket"] = action
        all_bucket_rows[action].append(rr)

for bucket, rows in all_bucket_rows.items():
    write_jsonl(OUT_DIR / f"{bucket}.jsonl", rows)

with REPORT.open("w", encoding="utf-8") as f:
    f.write("# Real Replay Mining v1 Decision Summary\n\n")

    f.write("## 1. Source Pools\n\n")
    f.write("| source_pool | rows |\n|---|---:|\n")
    for k, v in source_stats.items():
        f.write(f"| {k} | {v} |\n")

    f.write("\n## 2. Suggested Action Buckets\n\n")
    f.write("| bucket | rows | suggested_next_action |\n|---|---:|---|\n")

    action_desc = {
        "low_info_context_needed": "Do not expand SOP. Improve context retrieval / memory / query construction.",
        "merchant_fact_gap": "Do not train first. Build merchant/product/activity/fact layer or mock fact cards.",
        "taxonomy_or_label_gap": "Review label taxonomy. Do not treat as retrieval failure directly.",
        "retrieval_or_policy_priority_gap": "Inspect top cards and adjust retrieval priority / gate / policy precedence.",
        "platform_sop_or_retrieval_gap": "Review whether platform SOP exists or retrieval failed to recall it.",
        "dpo_drop_same_pair": "Drop from DPO.",
        "dpo_needs_manual_safety_review": "Manual safety review before DPO.",
        "dpo_drop_incomplete": "Drop incomplete DPO rows.",
        "dpo_needs_rewrite_or_drop": "Short pair. Rewrite or drop before training.",
        "dpo_keep_candidate": "Can enter DPO review queue.",
        "dpo_needs_manual_review": "Manual review needed.",
    }

    for bucket, rows in sorted(all_bucket_rows.items(), key=lambda x: len(x[1]), reverse=True):
        f.write(f"| {bucket} | {len(rows)} | {action_desc.get(bucket, '')} |\n")

    f.write("\n## 3. Key Decisions\n\n")
    f.write("1. Do not run SFT/DPO directly from the current real replay assets.\n")
    f.write("2. Most product/promotion/stock/gift/coupon cases should go to merchant fact modeling, not platform SOP expansion.\n")
    f.write("3. Weak-query cases should go to context/memory/query construction, not keyword rules.\n")
    f.write("4. Platform SOP/retrieval gap cases should be reviewed separately from merchant fact gaps.\n")
    f.write("5. DPO candidates require filtering and manual review before training.\n\n")

    f.write("## 4. Output Files\n\n")
    for bucket in sorted(all_bucket_rows):
        f.write(f"- `{OUT_DIR / (bucket + '.jsonl')}`\n")

print({
    "report": str(REPORT),
    "out_dir": str(OUT_DIR),
    "buckets": {k: len(v) for k, v in sorted(all_bucket_rows.items(), key=lambda x: len(x[1]), reverse=True)}
})
