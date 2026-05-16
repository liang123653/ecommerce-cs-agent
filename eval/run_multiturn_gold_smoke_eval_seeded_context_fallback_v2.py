# -*- coding: utf-8 -*-
import argparse
import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.answer_strategy import answer_with_strategy


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "database" / "ecommerce.db"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def get_table_columns(cur: sqlite3.Cursor, table: str) -> List[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def insert_flexible(cur: sqlite3.Cursor, table: str, record: Dict[str, Any]):
    cols = get_table_columns(cur, table)
    usable = {k: v for k, v in record.items() if k in cols}

    if not usable:
        raise RuntimeError(f"No usable columns for table={table}. record_keys={list(record.keys())}, table_cols={cols}")

    keys = list(usable.keys())
    placeholders = ",".join(["?"] * len(keys))
    sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})"
    cur.execute(sql, [usable[k] for k in keys])


def delete_seeded_rows(cur: sqlite3.Cursor, user_id: str):
    for table in ["conversation_messages", "conversation_summaries"]:
        cols = get_table_columns(cur, table)
        if "user_id" in cols:
            cur.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))


def summarize_seed_history(messages: List[Dict[str, str]]) -> str:
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    assistant_msgs = [m["content"] for m in messages if m.get("role") == "assistant"]

    parts = []
    if user_msgs:
        parts.append("用户历史咨询：" + "；".join(user_msgs[:3]))
    if assistant_msgs:
        parts.append("历史客服回复：" + "；".join(assistant_msgs[:3]))
    return "\n".join(parts) if parts else "无历史消息。"


def risk_tag_for(row: Dict[str, Any]) -> str:
    risk = row.get("expected_history_risk")
    if risk == "high":
        return "高风险; seeded_multiturn_gold"
    if risk == "medium":
        return "中风险; seeded_multiturn_gold"
    return "低风险; seeded_multiturn_gold"


def seed_case_history(row: Dict[str, Any], user_id: str, product_id: Optional[str] = None, order_id: Optional[str] = None):
    """
    将 gold case 的历史 turns 写入现有 memory backend 使用的 SQLite 表。
    只用于 eval，不作为线上写入逻辑。
    """
    messages = row.get("messages") or []
    history_messages = messages[:-1]

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    delete_seeded_rows(cur, user_id)

    base_time = datetime(2026, 1, 1, 9, 0, 0)
    session_id = f"seed_{row['eval_id']}"

    for idx, msg in enumerate(history_messages):
        created_at = (base_time + timedelta(seconds=idx)).isoformat(sep=" ")
        rec = {
            "user_id": user_id,
            "session_id": session_id,
            "conversation_id": session_id,
            "dialogue_id": session_id,
            "turn_id": idx + 1,
            "role": msg.get("role"),
            "content": msg.get("content"),
            "product_id": product_id,
            "order_id": order_id,
            "created_at": created_at,
            "source": "multiturn_gold_seed",
            "metadata": json.dumps(
                {
                    "eval_id": row.get("eval_id"),
                    "expected_behavior": row.get("expected_behavior"),
                    "expected_history_risk": row.get("expected_history_risk"),
                },
                ensure_ascii=False,
            ),
        }
        insert_flexible(cur, "conversation_messages", rec)

    # 写摘要，增强 query_summaries 召回。
    if history_messages:
        rec = {
            "user_id": user_id,
            "session_id": session_id,
            "conversation_id": session_id,
            "dialogue_id": session_id,
            "product_id": product_id,
            "order_id": order_id,
            "summary": summarize_seed_history(history_messages),
            "risk_tags": risk_tag_for(row),
            "created_at": (base_time + timedelta(seconds=100)).isoformat(sep=" "),
            "source": "multiturn_gold_seed",
            "metadata": json.dumps(
                {
                    "eval_id": row.get("eval_id"),
                    "expected_behavior": row.get("expected_behavior"),
                    "expected_history_risk": row.get("expected_history_risk"),
                },
                ensure_ascii=False,
            ),
        }
        insert_flexible(cur, "conversation_summaries", rec)

    con.commit()
    con.close()


def contains_any(text: str, bad_words: List[str]) -> List[str]:
    text = text or ""
    return [w for w in bad_words if w and w in text]


def check_behavior(row: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    expected = row.get("expected_behavior", "")
    reply = result.get("reply") or ""
    scene = result.get("scene")
    strategy = result.get("strategy")
    raw = result.get("raw_mainline") or {}
    hist = raw.get("history_context") or {}

    bad_hits = contains_any(reply, row.get("must_not_contain") or [])
    safe_pass = len(bad_hits) == 0

    behavior_pass = True
    behavior_reasons = []

    if expected in {"description_mismatch_or_handoff", "gift_description_mismatch"}:
        ok = (
            scene == "description_mismatch"
            or strategy == "RISK_HANDOFF"
            or ("核实" in reply and ("人工" in reply or "售后" in reply or "专员" in reply))
        )
        if not ok:
            behavior_pass = False
            behavior_reasons.append("expected_description_mismatch_or_handoff")

    elif expected == "return_exchange_safe":
        ok = (
            scene == "return_exchange"
            or "换货" in reply
            or "退货" in reply
            or "申请售后" in reply
            or "订单详情" in reply
        )
        if not ok:
            behavior_pass = False
            behavior_reasons.append("expected_return_exchange_safe")

    elif expected in {
        "context_dependent_price_protection",
        "context_dependent_express_ack",
        "context_dependent_quality_after_photo",
        "context_dependent_order_modify",
        "context_dependent_express_check",
        "context_dependent_missing_package",
        "context_dependent_return_condition",
        "context_dependent_product_knowledge",
        "context_dependent_refund_help",
        "context_dependent_logistics_followup",
    }:
        generic_fallback_markers = [
            "这个问题需要结合具体商品、订单或店铺配置确认",
            "麻烦您补充一下商品链接、订单号或具体需求",
        ]
        if any(x in reply for x in generic_fallback_markers) and not raw:
            behavior_pass = False
            behavior_reasons.append("generic_fallback_without_history_or_mainline")

    elif expected in {
        "shipping_delay_risk_handoff",
        "shipping_delay_fact_check",
        "logistics_risk_check",
        "express_commitment_check",
        "promotion_price_check",
        "quality_or_description_check",
        "price_or_order_check",
        "product_fact_or_description_check",
        "stock_shipping_check",
        "product_fact_check",
        "product_fact_no_overpromise",
    }:
        ok = any(x in reply for x in ["核实", "查看", "订单", "页面", "商品", "以实际", "人工", "售后"])
        if not ok:
            behavior_pass = False
            behavior_reasons.append("expected_fact_or_check_language")

    elif expected in {"small_talk_context_end", "small_talk_or_close"}:
        if len(reply) > 120:
            behavior_pass = False
            behavior_reasons.append("small_talk_reply_too_long")

    expected_risk = row.get("expected_history_risk")
    actual_risk = hist.get("risk_level")

    history_risk_pass = None
    if expected_risk == "high":
        history_risk_pass = actual_risk == "high"
    elif expected_risk == "medium":
        history_risk_pass = actual_risk in {"medium", "high"}
    elif expected_risk == "low":
        history_risk_pass = actual_risk in {"low", "medium", None, "unknown"}

    return {
        "safe_pass": safe_pass,
        "bad_hits": bad_hits,
        "behavior_pass": behavior_pass,
        "behavior_reasons": behavior_reasons,
        "expected_history_risk": expected_risk,
        "actual_history_risk": actual_risk,
        "history_risk_pass": history_risk_pass,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/eval/multiturn/multiturn_gold_smoke_v1.jsonl")
    parser.add_argument("--out", default="data/eval/multiturn/multiturn_gold_smoke_v1_seeded_context_fallback_v2_results.jsonl")
    parser.add_argument("--summary", default="data/eval/multiturn/multiturn_gold_smoke_v1_seeded_context_fallback_v2_summary.json")
    parser.add_argument("--user_prefix", default="mt_gold_seed_user")
    args = parser.parse_args()

    os.environ["USE_CONVERSATION_MEMORY"] = "1"

    rows = load_jsonl(Path(args.input))
    out_path = Path(args.out)
    summary_path = Path(args.summary)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    counters = Counter()
    by_expected = defaultdict(Counter)

    with out_path.open("w", encoding="utf-8") as out_f:
        for row in rows:
            user_id = f"{args.user_prefix}_{row['eval_id']}"
            q = row["retrieval_query"]

            try:
                seed_case_history(row, user_id=user_id)
                result = answer_with_strategy(q, user_id=user_id)
                runtime_ok = True
                error = None
            except Exception as e:
                result = {}
                runtime_ok = False
                error = f"{type(e).__name__}: {e}"

            check = check_behavior(row, result) if runtime_ok else {
                "safe_pass": False,
                "bad_hits": [],
                "behavior_pass": False,
                "behavior_reasons": ["runtime_error"],
                "expected_history_risk": row.get("expected_history_risk"),
                "actual_history_risk": None,
                "history_risk_pass": False,
            }

            raw = result.get("raw_mainline") or {}
            hist = raw.get("history_context") or {}

            record = {
                "eval_id": row.get("eval_id"),
                "retrieval_query": q,
                "expected_behavior": row.get("expected_behavior"),
                "expected_history_risk": row.get("expected_history_risk"),
                "runtime_ok": runtime_ok,
                "error": error,
                "strategy": result.get("strategy"),
                "mainline_used": result.get("mainline_used"),
                "scene": result.get("scene"),
                "policy_file": result.get("policy_file"),
                "raw_user_id": raw.get("user_id"),
                "history_has_history": hist.get("has_history"),
                "history_risk_level": hist.get("risk_level"),
                "history_risk_reason": hist.get("risk_reason"),
                "history_summary": hist.get("summary"),
                "safe_pass": check["safe_pass"],
                "bad_hits": check["bad_hits"],
                "behavior_pass": check["behavior_pass"],
                "behavior_reasons": check["behavior_reasons"],
                "history_risk_pass": check["history_risk_pass"],
                "reply": result.get("reply"),
                "note": row.get("note"),
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

            counters["total"] += 1
            counters["runtime_ok"] += int(runtime_ok)
            counters["safe_pass"] += int(check["safe_pass"])
            counters["behavior_pass"] += int(check["behavior_pass"])
            counters["mainline_used"] += int(bool(result.get("mainline_used")))
            counters["history_has_history"] += int(bool(hist.get("has_history")))
            counters["history_high"] += int(hist.get("risk_level") == "high")

            if check["history_risk_pass"] is not None:
                counters["history_risk_checked"] += 1
                counters["history_risk_pass"] += int(bool(check["history_risk_pass"]))

            key = row.get("expected_behavior")
            by_expected[key]["count"] += 1
            by_expected[key]["safe_pass"] += int(check["safe_pass"])
            by_expected[key]["behavior_pass"] += int(check["behavior_pass"])

    total = counters["total"] or 1
    summary = {
        "decision": "MULTITURN_GOLD_SMOKE_EVAL_SEEDED_CONTEXT_FALLBACK_V2_COMPLETED",
        "input": args.input,
        "result_file": args.out,
        "sample_size": counters["total"],
        "overall": {
            "runtime_success_rate": round(counters["runtime_ok"] / total, 4),
            "safe_reply_rate": round(counters["safe_pass"] / total, 4),
            "behavior_pass_rate": round(counters["behavior_pass"] / total, 4),
            "mainline_usage_rate": round(counters["mainline_used"] / total, 4),
            "history_has_history_rate": round(counters["history_has_history"] / total, 4),
            "history_high_rate": round(counters["history_high"] / total, 4),
            "history_risk_pass_rate": (
                round(counters["history_risk_pass"] / counters["history_risk_checked"], 4)
                if counters["history_risk_checked"] else None
            ),
        },
        "by_expected_behavior": {
            k: {
                "count": v["count"],
                "safe_pass_rate": round(v["safe_pass"] / v["count"], 4),
                "behavior_pass_rate": round(v["behavior_pass"] / v["count"], 4),
            }
            for k, v in sorted(by_expected.items())
        },
    }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
