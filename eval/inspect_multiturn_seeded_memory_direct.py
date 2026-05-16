# -*- coding: utf-8 -*-
import json
from collections import Counter
from pathlib import Path

from memory.conversation_retriever import retrieve_conversation_context

p = Path("data/eval/multiturn/multiturn_gold_smoke_v1.jsonl")
rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

counter = Counter()
out = Path("data/eval/multiturn/multiturn_gold_smoke_v1_direct_memory_inspect.jsonl")

with out.open("w", encoding="utf-8") as f:
    for row in rows:
        user_id = f"mt_gold_seed_user_{row['eval_id']}"
        q = row["retrieval_query"]
        ctx = retrieve_conversation_context(user_id=user_id, query=q, top_k=5)

        rec = {
            "eval_id": row["eval_id"],
            "query": q,
            "expected_history_risk": row.get("expected_history_risk"),
            "has_history": ctx.get("has_history"),
            "risk_level": ctx.get("risk_level"),
            "risk_reason": ctx.get("risk_reason"),
            "summary": ctx.get("summary"),
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        counter["total"] += 1
        counter["has_history"] += int(bool(ctx.get("has_history")))
        counter[f"risk_{ctx.get('risk_level')}"] += 1

summary = {
    "total": counter["total"],
    "has_history_rate": round(counter["has_history"] / counter["total"], 4),
    "risk_distribution": {
        k.replace("risk_", ""): v
        for k, v in counter.items()
        if k.startswith("risk_")
    },
    "out": str(out),
}

print(json.dumps(summary, ensure_ascii=False, indent=2))
