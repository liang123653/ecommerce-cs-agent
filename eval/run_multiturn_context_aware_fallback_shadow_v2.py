# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import Counter, defaultdict

from memory.conversation_retriever import retrieve_conversation_context


base = Path("data/eval/multiturn")
gold_path = base / "multiturn_gold_smoke_v1.jsonl"
out_path = base / "multiturn_context_aware_fallback_shadow_v2.jsonl"
summary_path = base / "multiturn_context_aware_fallback_shadow_v2_summary.json"

rows = [
    json.loads(x)
    for x in gold_path.read_text(encoding="utf-8").splitlines()
    if x.strip()
]


def contains_any(text, words):
    return [w for w in words if w and w in text]


def has_high_risk_summary_tag(history_context):
    """
    不做业务关键词扩展，只读取历史摘要里已有的风险标签。
    """
    for s in history_context.get("summaries") or []:
        if "高风险" in (s.get("risk_tags") or ""):
            return True
    return False


def build_context_aware_fallback(query, history_context, expected_behavior=None):
    """
    Shadow-only guarded fallback v2.
    不做 scene 分类，不调用旧 mainline retriever，不承诺结果。
    v2 改动：如果历史摘要已有高风险标签，即使 retriever risk_level=medium，也使用严格核实/人工升级模板。
    """
    risk = history_context.get("risk_level")
    has_history = history_context.get("has_history")
    summary_marked_high = has_high_risk_summary_tag(history_context)

    if not has_history:
        return (
            "您好，这个问题需要结合具体商品、订单或历史沟通记录确认。"
            "麻烦您补充一下订单号、商品链接或相关截图，我再帮您核实。"
        )

    if risk == "high" or summary_marked_high:
        return (
            "抱歉给您带来困扰。这个情况需要结合前面的沟通记录、商品页面信息、订单信息和您收到的实物情况一起核实。"
            "我会把历史咨询记录一并作为核实依据，但在确认前不能直接认定责任，也不能直接承诺退款、赔偿、补发或其他处理结果。"
            "麻烦您提供订单号、商品页面截图、实物照片或相关凭证；如果核实存在售前答复、页面说明、活动赠品或实际商品不一致，建议升级人工或售后专员按平台规则处理。"
        )

    if risk == "medium":
        return (
            "我看到这个问题和前面的沟通有关。为了避免让您重复描述，我会结合历史咨询内容一起帮您核实。"
            "不过具体处理结果还需要以订单状态、商品页面、活动规则或实际凭证为准，不能直接承诺一定可以处理。"
            "麻烦您补充订单号、商品链接或相关截图，我再帮您继续确认。"
        )

    return (
        "我理解您是在接着前面的问题继续确认。"
        "我会结合前面的沟通记录帮您看一下，但具体结果还需要以订单、商品页面或实际状态为准。"
        "麻烦您补充一下订单号或商品信息，我再帮您核实。"
    )


def check_behavior(row, reply, history_context):
    expected = row.get("expected_behavior", "")
    bad_hits = contains_any(reply, row.get("must_not_contain") or [])
    safe_pass = len(bad_hits) == 0

    behavior_pass = True
    reasons = []

    # 高风险/描述不符类：要有核实 + 不直接认责/承诺 + 人工/售后倾向。
    if expected in {
        "description_mismatch_or_handoff",
        "description_mismatch_or_quality",
        "gift_description_mismatch",
        "quality_or_description_check",
    }:
        ok = (
            "核实" in reply
            and ("不能直接认定责任" in reply or "不能直接承诺" in reply)
            and ("人工" in reply or "售后" in reply)
        )
        if not ok:
            behavior_pass = False
            reasons.append("expected_risk_context_handoff_language")

    # 低信息承接类：不能要求用户完全重说，要体现“结合前面沟通”。
    elif expected.startswith("context_dependent") or expected in {
        "stock_shipping_check",
        "return_exchange_safe",
        "order_note_or_gift_check",
        "price_or_order_check",
        "express_commitment_check",
    }:
        ok = (
            "前面" in reply
            or "历史" in reply
            or "沟通" in reply
            or "不让您重复" in reply
        )
        if not ok:
            behavior_pass = False
            reasons.append("expected_context_acknowledgement")

    # 结束语类：fallback 可能不该触发，先不强判失败。
    elif expected in {"small_talk_context_end", "small_talk_or_close"}:
        if len(reply) > 180:
            behavior_pass = False
            reasons.append("small_talk_fallback_too_long")

    return {
        "safe_pass": safe_pass,
        "bad_hits": bad_hits,
        "behavior_pass": behavior_pass,
        "behavior_reasons": reasons,
    }


counter = Counter()
by_expected = defaultdict(Counter)

with out_path.open("w", encoding="utf-8") as f:
    for row in rows:
        user_id = f"mt_gold_seed_user_{row['eval_id']}"
        query = row["retrieval_query"]
        history_context = retrieve_conversation_context(user_id=user_id, query=query, top_k=5)

        reply = build_context_aware_fallback(
            query=query,
            history_context=history_context,
            expected_behavior=row.get("expected_behavior"),
        )

        check = check_behavior(row, reply, history_context)

        rec = {
            "eval_id": row["eval_id"],
            "query": query,
            "expected_behavior": row.get("expected_behavior"),
            "expected_history_risk": row.get("expected_history_risk"),
            "history_has": history_context.get("has_history"),
            "history_risk": history_context.get("risk_level"),
            "history_reason": history_context.get("risk_reason"),
            "fallback_reply": reply,
            "safe_pass": check["safe_pass"],
            "bad_hits": check["bad_hits"],
            "behavior_pass": check["behavior_pass"],
            "behavior_reasons": check["behavior_reasons"],
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        counter["total"] += 1
        counter["history_has"] += int(bool(history_context.get("has_history")))
        counter["history_high"] += int(history_context.get("risk_level") == "high")
        counter["safe_pass"] += int(check["safe_pass"])
        counter["behavior_pass"] += int(check["behavior_pass"])

        key = row.get("expected_behavior")
        by_expected[key]["count"] += 1
        by_expected[key]["safe_pass"] += int(check["safe_pass"])
        by_expected[key]["behavior_pass"] += int(check["behavior_pass"])

summary = {
    "decision": "MULTITURN_CONTEXT_AWARE_FALLBACK_SHADOW_V2_COMPLETED",
    "sample_size": counter["total"],
    "overall": {
        "history_has_rate": round(counter["history_has"] / counter["total"], 4),
        "history_high_rate": round(counter["history_high"] / counter["total"], 4),
        "safe_reply_rate": round(counter["safe_pass"] / counter["total"], 4),
        "behavior_pass_rate": round(counter["behavior_pass"] / counter["total"], 4),
    },
    "by_expected_behavior": {
        k: {
            "count": v["count"],
            "safe_pass_rate": round(v["safe_pass"] / v["count"], 4),
            "behavior_pass_rate": round(v["behavior_pass"] / v["count"], 4),
        }
        for k, v in sorted(by_expected.items())
    },
    "files": {
        "result_file": str(out_path),
        "summary_file": str(summary_path),
    },
}

summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
