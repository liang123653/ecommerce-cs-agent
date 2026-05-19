# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import Counter, defaultdict

MAIN = Path("data/eval/phase15/phase15d_context_query_strategy_best_of_variants.jsonl")
DPO = Path("data/processed/real_dialogues/dpo_pairs_candidate.jsonl")

OUT_DIR = Path("data/eval/real_replay_mining_v1")
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT = Path("docs/REAL_REPLAY_MINING_V1_REPORT.md")
REPORT.parent.mkdir(parents=True, exist_ok=True)

NO_HIT_OUT = OUT_DIR / "no_hit_or_weak_query_sample.jsonl"
SCENE_MISMATCH_OUT = OUT_DIR / "scene_mismatch_sample.jsonl"
LOW_SCORE_OUT = OUT_DIR / "low_score_sample.jsonl"
DPO_AUDIT_SAMPLE_OUT = OUT_DIR / "dpo_candidate_audit_sample.jsonl"


def read_jsonl(path: Path, limit=None):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            if limit and len(rows) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                obj["_line_no"] = i
                rows.append(obj)
            except Exception:
                continue
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


rows = read_jsonl(MAIN)

hit_counter = Counter()
scene_counter = Counter()
top1_scene_counter = Counter()
strategy_counter = Counter()
source_counter = Counter()

no_hit_or_weak = []
scene_mismatch = []
low_score = []

for r in rows:
    hit = r.get("hit_status") or "unknown"
    hit_counter[hit] += 1

    scene = r.get("expected_scene") or "unknown"
    top1_scene = r.get("top1_scene") or "unknown"
    strategy = r.get("chosen_strategy") or "unknown"
    source = r.get("source") or "unknown"

    scene_counter[scene] += 1
    top1_scene_counter[top1_scene] += 1
    strategy_counter[strategy] += 1
    source_counter[source] += 1

    score = safe_float(r.get("top1_score"))

    if hit in {"no_hit", "weak_query"} or not r.get("top1_id"):
        no_hit_or_weak.append(r)

    if hit == "scene_mismatch" or (
        scene not in {"", "unknown", None}
        and top1_scene not in {"", "unknown", None}
        and scene != top1_scene
    ):
        scene_mismatch.append(r)

    if 0 < score < 15:
        low_score.append(r)


# 排序：优先高信息 query，而不是“是的/对”
def info_rank(r):
    q = r.get("retrieval_query") or r.get("last_user_query") or r.get("query") or ""
    return (len(q), safe_float(r.get("query_info_score")), safe_float(r.get("top1_score")))


no_hit_or_weak_sorted = sorted(no_hit_or_weak, key=info_rank, reverse=True)
scene_mismatch_sorted = sorted(scene_mismatch, key=info_rank, reverse=True)
low_score_sorted = sorted(low_score, key=info_rank, reverse=True)

write_jsonl(NO_HIT_OUT, no_hit_or_weak_sorted[:300])
write_jsonl(SCENE_MISMATCH_OUT, scene_mismatch_sorted[:300])
write_jsonl(LOW_SCORE_OUT, low_score_sorted[:300])


# DPO candidate audit sample
dpo_rows = read_jsonl(DPO)
dpo_issue_counter = Counter()
dpo_samples = []

for r in dpo_rows:
    prompt = r.get("prompt") or ""
    chosen = r.get("chosen") or ""
    rejected = r.get("rejected") or ""
    issues = []

    if not prompt.strip():
        issues.append("empty_prompt")
    if not chosen.strip():
        issues.append("empty_chosen")
    if not rejected.strip():
        issues.append("empty_rejected")
    if chosen.strip() == rejected.strip():
        issues.append("same_chosen_rejected")
    if len(chosen) < 15:
        issues.append("chosen_too_short")
    if len(rejected) < 15:
        issues.append("rejected_too_short")

    # 安全红线粗筛，不作为最终审核，只用于发现明显坏样本
    risky_phrases = ["一定退款", "必须赔偿", "肯定补发", "一定补偿", "百分百"]
    if any(x in chosen for x in risky_phrases):
        issues.append("chosen_possible_overpromise")

    if issues:
        for it in issues:
            dpo_issue_counter[it] += 1

    if len(dpo_samples) < 300:
        dpo_samples.append({
            "line_no": r.get("_line_no"),
            "issues": issues,
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
            "meta": r.get("meta"),
        })

write_jsonl(DPO_AUDIT_SAMPLE_OUT, dpo_samples)


def pct(n, d):
    return f"{(n / d * 100):.2f}%" if d else "0.00%"


with REPORT.open("w", encoding="utf-8") as f:
    f.write("# Real Replay Mining v1 Report\n\n")

    f.write("## 1. Input Files\n\n")
    f.write(f"- main_replay: `{MAIN}`\n")
    f.write(f"- dpo_candidates: `{DPO}`\n\n")

    f.write("## 2. Main Replay Overview\n\n")
    f.write(f"- total_rows: {len(rows)}\n")
    f.write(f"- no_hit_or_weak_count: {len(no_hit_or_weak)} ({pct(len(no_hit_or_weak), len(rows))})\n")
    f.write(f"- scene_mismatch_count: {len(scene_mismatch)} ({pct(len(scene_mismatch), len(rows))})\n")
    f.write(f"- low_score_count: {len(low_score)} ({pct(len(low_score), len(rows))})\n\n")

    f.write("### hit_status distribution\n\n")
    f.write("| hit_status | count | rate |\n|---|---:|---:|\n")
    for k, v in hit_counter.most_common():
        f.write(f"| {k} | {v} | {pct(v, len(rows))} |\n")

    f.write("\n### expected_scene distribution top 30\n\n")
    f.write("| scene | count | rate |\n|---|---:|---:|\n")
    for k, v in scene_counter.most_common(30):
        f.write(f"| {k} | {v} | {pct(v, len(rows))} |\n")

    f.write("\n### top1_scene distribution top 30\n\n")
    f.write("| top1_scene | count | rate |\n|---|---:|---:|\n")
    for k, v in top1_scene_counter.most_common(30):
        f.write(f"| {k} | {v} | {pct(v, len(rows))} |\n")

    f.write("\n### chosen_strategy distribution\n\n")
    f.write("| strategy | count | rate |\n|---|---:|---:|\n")
    for k, v in strategy_counter.most_common():
        f.write(f"| {k} | {v} | {pct(v, len(rows))} |\n")

    f.write("\n## 3. Output Pools\n\n")
    f.write(f"- no_hit_or_weak sample: `{NO_HIT_OUT}`\n")
    f.write(f"- scene_mismatch sample: `{SCENE_MISMATCH_OUT}`\n")
    f.write(f"- low_score sample: `{LOW_SCORE_OUT}`\n")
    f.write(f"- dpo audit sample: `{DPO_AUDIT_SAMPLE_OUT}`\n\n")

    f.write("## 4. DPO Candidate Overview\n\n")
    f.write(f"- dpo_candidate_rows: {len(dpo_rows)}\n\n")

    f.write("### DPO automatic issue counts\n\n")
    f.write("| issue | count |\n|---|---:|\n")
    for k, v in dpo_issue_counter.most_common():
        f.write(f"| {k} | {v} |\n")

    f.write("\n## 5. Interpretation\n\n")
    f.write("- This report is a lightweight real replay mining report.\n")
    f.write("- It does not call LLM generation.\n")
    f.write("- It should be used to decide which samples enter SOP review, SFT data construction, or DPO pair audit.\n")
    f.write("- DPO candidates are not treated as training-ready until reviewed.\n")

print({
    "main_rows": len(rows),
    "no_hit_or_weak": len(no_hit_or_weak),
    "scene_mismatch": len(scene_mismatch),
    "low_score": len(low_score),
    "dpo_rows": len(dpo_rows),
    "report": str(REPORT),
    "outputs": {
        "no_hit_or_weak": str(NO_HIT_OUT),
        "scene_mismatch": str(SCENE_MISMATCH_OUT),
        "low_score": str(LOW_SCORE_OUT),
        "dpo_audit_sample": str(DPO_AUDIT_SAMPLE_OUT),
    }
})
