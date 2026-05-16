import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("USE_VECTOR_RAG", "1")
os.environ.setdefault("VECTOR_RAG_BACKEND", "bge")

from rag.vector_retriever import retrieve_policy_vector


EVAL_PATH = ROOT_DIR / "data" / "eval" / "eval_cases.jsonl"
REPORT_DIR = ROOT_DIR / "eval" / "outputs"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_cases():
    cases = []
    with EVAL_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def main():
    cases = load_cases()
    rows = []
    correct = 0

    for case in cases:
        result = retrieve_policy_vector(case["query"], top_k=3)
        ok = result["scene"] == case["expected_scene"]
        correct += int(ok)

        rows.append({
            "query": case["query"],
            "category": case.get("category", ""),
            "expected_scene": case["expected_scene"],
            "pred_scene": result["scene"],
            "expected_file": case["expected_file"],
            "top1_file": result["file_name"],
            "ok": ok,
            "keyword_scene": result.get("keyword_scene"),
            "top_chunks": [
                {
                    "file_name": c["file_name"],
                    "score": round(c["score"], 4),
                    "raw_score": round(c.get("raw_score", c["score"]), 4),
                    "bonus": round(c.get("rerank_bonus", 0.0), 4),
                }
                for c in result.get("chunks", [])
            ],
        })

    acc = correct / len(cases) if cases else 0.0

    out_json = REPORT_DIR / "retrieval_eval_results.json"
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = REPORT_DIR / "retrieval_eval_report.md"
    lines = []
    lines.append("# RAG 检索评测报告\n")
    lines.append(f"- 样本数：{len(cases)}")
    lines.append(f"- Top1 场景准确率：{acc:.2%}\n")
    lines.append("| 类别 | 问题 | 期望场景 | 预测场景 | Top1 文件 | 是否正确 |")
    lines.append("|---|---|---|---|---|---|")

    for r in rows:
        flag = "✅" if r["ok"] else "❌"
        lines.append(
            f"| {r['category']} | {r['query']} | {r['expected_scene']} | {r['pred_scene']} | {r['top1_file']} | {flag} |"
        )

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 80)
    print("RAG 检索评测完成")
    print(f"样本数: {len(cases)}")
    print(f"Top1 场景准确率: {acc:.2%}")
    print(f"报告: {out_md}")
    print(f"明细: {out_json}")

    for r in rows:
        flag = "✅" if r["ok"] else "❌"
        print(f"{flag} {r['query']} -> {r['pred_scene']} / {r['top1_file']}")


if __name__ == "__main__":
    main()
