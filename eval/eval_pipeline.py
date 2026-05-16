import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("USE_VECTOR_RAG", "1")
os.environ.setdefault("VECTOR_RAG_BACKEND", "bge")

from app.pipeline_llm import answer_with_llm


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


def check_reply(reply: str, must_include: list[str], must_not_include: list[str]):
    missing = [w for w in must_include if w not in reply]
    forbidden = [w for w in must_not_include if w in reply]
    return {
        "rule_hit_ok": len(missing) == 0,
        "safety_ok": len(forbidden) == 0,
        "missing": missing,
        "forbidden": forbidden,
    }


def main():
    cases = load_cases()
    rows = []

    for i, case in enumerate(cases, 1):
        print("=" * 80)
        print(f"[{i}/{len(cases)}] {case['query']}")

        result = answer_with_llm(case["query"])
        reply = result["reply"]
        check = check_reply(reply, case.get("must_include", []), case.get("must_not_include", []))

        scene_ok = result["scene"] == case["expected_scene"]
        file_ok = result["policy_file"] == case["expected_file"]
        overall_ok = scene_ok and file_ok and check["rule_hit_ok"] and check["safety_ok"]

        row = {
            "query": case["query"],
            "category": case.get("category", ""),
            "expected_scene": case["expected_scene"],
            "pred_scene": result["scene"],
            "expected_file": case["expected_file"],
            "policy_file": result["policy_file"],
            "scene_ok": scene_ok,
            "file_ok": file_ok,
            "rule_hit_ok": check["rule_hit_ok"],
            "safety_ok": check["safety_ok"],
            "overall_ok": overall_ok,
            "missing": check["missing"],
            "forbidden": check["forbidden"],
            "fallback_used": result.get("fallback_used", False),
            "validation_errors": result.get("validation_errors", []),
            "reply": reply,
            "llm_reply": result.get("llm_reply", ""),
            "retrieved_chunks": [
                {
                    "file_name": c["file_name"],
                    "score": round(c["score"], 4),
                    "raw_score": round(c.get("raw_score", c["score"]), 4),
                    "bonus": round(c.get("rerank_bonus", 0.0), 4),
                }
                for c in result.get("retrieved_chunks", [])
            ],
        }
        rows.append(row)

        print("场景:", result["scene"])
        print("文件:", result["policy_file"])
        print("兜底:", result.get("fallback_used", False))
        print("通过:", overall_ok)
        if check["missing"]:
            print("缺失:", check["missing"])
        if check["forbidden"]:
            print("违禁:", check["forbidden"])

    total = len(rows)
    scene_acc = sum(r["scene_ok"] for r in rows) / total
    file_acc = sum(r["file_ok"] for r in rows) / total
    rule_hit_rate = sum(r["rule_hit_ok"] for r in rows) / total
    safety_rate = sum(r["safety_ok"] for r in rows) / total
    overall_rate = sum(r["overall_ok"] for r in rows) / total
    fallback_rate = sum(r["fallback_used"] for r in rows) / total

    summary = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "scene_acc": scene_acc,
        "file_acc": file_acc,
        "rule_hit_rate": rule_hit_rate,
        "safety_rate": safety_rate,
        "overall_rate": overall_rate,
        "fallback_rate": fallback_rate,
    }

    out_jsonl = REPORT_DIR / "pipeline_eval_results.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    out_summary = REPORT_DIR / "pipeline_eval_summary.json"
    out_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = REPORT_DIR / "pipeline_eval_report.md"
    lines = []
    lines.append("# 客服大模型业务链路评测报告\n")
    lines.append(f"- 评测时间：{summary['time']}")
    lines.append(f"- 样本数：{total}")
    lines.append(f"- 场景识别准确率：{scene_acc:.2%}")
    lines.append(f"- SOP 文件命中率：{file_acc:.2%}")
    lines.append(f"- 规则要点命中率：{rule_hit_rate:.2%}")
    lines.append(f"- 安全约束通过率：{safety_rate:.2%}")
    lines.append(f"- 综合通过率：{overall_rate:.2%}")
    lines.append(f"- 规则兜底触发率：{fallback_rate:.2%}\n")

    lines.append("## 明细结果\n")
    lines.append("| 类别 | 用户问题 | 预测场景 | SOP | 要点命中 | 安全通过 | 兜底 | 综合 |")
    lines.append("|---|---|---|---|---|---|---|---|")

    for r in rows:
        lines.append(
            f"| {r['category']} | {r['query']} | {r['pred_scene']} | {r['policy_file']} | "
            f"{'✅' if r['rule_hit_ok'] else '❌'} | "
            f"{'✅' if r['safety_ok'] else '❌'} | "
            f"{'是' if r['fallback_used'] else '否'} | "
            f"{'✅' if r['overall_ok'] else '❌'} |"
        )

    lines.append("\n## Badcase 分析\n")
    badcases = [r for r in rows if not r["overall_ok"]]
    if not badcases:
        lines.append("本轮评测未发现综合失败样本。")
    else:
        for r in badcases:
            lines.append(f"\n### {r['query']}")
            lines.append(f"- 预测场景：{r['pred_scene']}")
            lines.append(f"- 命中 SOP：{r['policy_file']}")
            lines.append(f"- 缺失要点：{r['missing']}")
            lines.append(f"- 违禁表达：{r['forbidden']}")
            lines.append(f"- 是否兜底：{r['fallback_used']}")
            lines.append(f"- 最终回复：{r['reply']}")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 80)
    print("业务链路评测完成")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"报告: {out_md}")
    print(f"明细: {out_jsonl}")


if __name__ == "__main__":
    main()
