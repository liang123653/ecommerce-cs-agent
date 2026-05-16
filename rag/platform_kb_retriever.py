from __future__ import annotations

import json, re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHUNKS = ROOT / "data" / "platform_kb" / "chunks.jsonl"

def load_chunks(path: Path = DEFAULT_CHUNKS) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def tokens(text: str) -> List[str]:
    text = re.sub(r"\s+", "", (text or "").lower())
    return [text[i:i+2] for i in range(max(0, len(text)-1))] + re.findall(r"[a-zA-Z0-9_]+", text)

def score(query: str, content: str) -> float:
    q = tokens(query)
    c = (content or "").lower()
    s = sum(1 for t in q if t and t in c)
    for w in ["退款", "退货", "换货", "发货", "物流", "驿站", "发票", "质量", "描述不符", "价保", "赠品", "优惠"]:
        if w in query and w in content:
            s += 3
    return float(s)

def retrieve_platform_kb(
    query: str,
    scene: Optional[str] = None,
    top_k: int = 5,
    chunks_path: str | Path = DEFAULT_CHUNKS,
    approved_only: bool = True,
):
    rows = load_chunks(Path(chunks_path))
    scored = []

    for r in rows:
        if approved_only and r.get("status") != "approved":
            continue
        if scene and r.get("scene") != scene:
            continue

        base_score = score(query, r.get("content", ""))

        authority = r.get("authority", "")
        source_type = r.get("source_type", "")

        authority_boost = 0.0
        if authority == "official_public":
            authority_boost = 3.0
        elif authority == "official_api_doc":
            authority_boost = 2.0
        elif source_type == "merchant_policy":
            authority_boost = 1.0
        elif authority == "sample":
            authority_boost = -1.0

        final_score = base_score + authority_boost

        if final_score > 0:
            item = dict(r)
            item["score"] = final_score
            item["base_score"] = base_score
            item["authority_boost"] = authority_boost
            scored.append(item)

    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--scene", default="")
    ap.add_argument("--top_k", type=int, default=5)
    args = ap.parse_args()
    for r in retrieve_platform_kb(args.query, scene=args.scene or None, top_k=args.top_k):
        print("=" * 80)
        print(r["chunk_id"], r["scene"], r["score"], r.get("source_title"))
        print(r["content"])
