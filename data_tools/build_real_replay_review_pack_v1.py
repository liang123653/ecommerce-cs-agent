# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import Counter

BASE = Path("data/eval/real_replay_mining_v1")

INPUTS = {
    "no_hit_or_weak": BASE / "no_hit_or_weak_query_sample.jsonl",
    "scene_mismatch": BASE / "scene_mismatch_sample.jsonl",
    "low_score": BASE / "low_score_sample.jsonl",
    "dpo_audit": BASE / "dpo_candidate_audit_sample.jsonl",
}

OUT = Path("docs/REAL_REPLAY_MINING_V1_REVIEW_PACK.md")


def read_jsonl(path, limit=80):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if len(rows) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def brief_cards(cards, limit=3):
    if not isinstance(cards, list):
        return ""
    out = []
    for c in cards[:limit]:
        if not isinstance(c, dict):
            continue
        cid = c.get("id") or c.get("chunk_id") or ""
        scene = c.get("scene") or ""
        score = c.get("score") or c.get("raw_score") or ""
        out.append(f"{cid}/{scene}/{score}")
    return "<br>".join(out)


def clean(s, n=120):
    s = "" if s is None else str(s)
    s = s.replace("\n", " ").replace("|", "｜")
    return s[:n]


with OUT.open("w", encoding="utf-8") as f:
    f.write("# Real Replay Mining v1 Review Pack\n\n")
    f.write("## 使用说明\n\n")
    f.write("本审核包不是让你为单个样本补关键词，而是做 cluster-level / category-level 决策。\n\n")
    f.write("重点判断每条样本属于哪类：\n\n")
    f.write("- `low_info_context_needed`：当前轮信息不足，需要上下文，不应直接扩 SOP\n")
    f.write("- `taxonomy_gap`：标签体系不对齐，expected_scene 比当前系统更细\n")
    f.write("- `merchant_fact_gap`：需要店铺/商品/活动/库存/快递配置事实\n")
    f.write("- `platform_sop_gap`：确实缺平台 SOP\n")
    f.write("- `retrieval_gap`：SOP 有但检索没召回\n")
    f.write("- `label_noise`：expected_scene 或样本本身不可靠\n")
    f.write("- `dpo_keep`：可以进入 DPO\n")
    f.write("- `dpo_drop`：不能进入 DPO\n\n")

    for name, path in INPUTS.items():
        rows = read_jsonl(path, limit=80)

        f.write(f"\n# {name}\n\n")
        f.write(f"- source: `{path}`\n")
        f.write(f"- shown_rows: {len(rows)}\n\n")

        if name == "dpo_audit":
            issue_counter = Counter()
            for r in rows:
                for it in r.get("issues") or []:
                    issue_counter[it] += 1
            f.write("## issue distribution in shown rows\n\n")
            f.write("| issue | count |\n|---|---:|\n")
            for k, v in issue_counter.most_common():
                f.write(f"| {k} | {v} |\n")
            f.write("\n")

            f.write("| idx | issues | prompt | chosen | rejected | suggested_decision |\n")
            f.write("|---:|---|---|---|---|---|\n")
            for i, r in enumerate(rows, 1):
                f.write(
                    f"| {i} | {clean(','.join(r.get('issues') or []), 80)} "
                    f"| {clean(r.get('prompt'), 100)} "
                    f"| {clean(r.get('chosen'), 100)} "
                    f"| {clean(r.get('rejected'), 100)} "
                    f"|  |\n"
                )
        else:
            scene_counter = Counter((r.get("expected_scene") or "unknown") for r in rows)
            hit_counter = Counter((r.get("hit_status") or "unknown") for r in rows)

            f.write("## expected_scene distribution in shown rows\n\n")
            f.write("| scene | count |\n|---|---:|\n")
            for k, v in scene_counter.most_common(20):
                f.write(f"| {k} | {v} |\n")

            f.write("\n## hit_status distribution in shown rows\n\n")
            f.write("| hit_status | count |\n|---|---:|\n")
            for k, v in hit_counter.most_common():
                f.write(f"| {k} | {v} |\n")

            f.write("\n## review table\n\n")
            f.write("| idx | retrieval_query | expected_scene | hit_status | top1_scene | top1_score | top_cards | suggested_bucket | note |\n")
            f.write("|---:|---|---|---|---|---:|---|---|---|\n")
            for i, r in enumerate(rows, 1):
                f.write(
                    f"| {i} "
                    f"| {clean(r.get('retrieval_query') or r.get('query') or r.get('last_user_query'), 100)} "
                    f"| {clean(r.get('expected_scene'), 40)} "
                    f"| {clean(r.get('hit_status'), 30)} "
                    f"| {clean(r.get('top1_scene'), 40)} "
                    f"| {r.get('top1_score') or 0} "
                    f"| {brief_cards(r.get('top_cards'))} "
                    f"|  "
                    f"|  |\n"
                )

print({"out": str(OUT)})
