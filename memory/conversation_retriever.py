from typing import Optional, Dict, Any, List
from memory.conversation_store import query_messages, query_summaries

RISK_KEYWORDS = [
    "支持", "不支持", "可以", "不能", "承诺", "保证",
    "主动降噪", "降噪", "防水", "保修", "质保", "正品", "发票",
    "赠品", "优惠", "尺码", "材质", "颜色", "保质期",
]

REFERENCE_HISTORY_WORDS = [
    "之前", "当时", "上次", "你们说", "客服说", "问过",
]

DISPUTE_WORDS = [
    "不一致", "不符合", "不是", "根本没有", "没有这个功能",
    "不支持", "骗人", "骗我", "和说的不一样", "描述不符",
    "虚假宣传", "承诺不一致",
]

SHARED_ATTRIBUTE_WORDS = [
    "主动降噪", "降噪", "防水", "发票", "尺码", "颜色",
    "材质", "保修", "质保", "优惠", "赠品", "保质期",
]


def keyword_score(text: str, query: str) -> int:
    score = 0

    for kw in RISK_KEYWORDS:
        if kw in text:
            score += 1

    for kw in REFERENCE_HISTORY_WORDS:
        if kw in query:
            score += 1

    for kw in DISPUTE_WORDS:
        if kw in query:
            score += 2

    for kw in SHARED_ATTRIBUTE_WORDS:
        if kw in query and kw in text:
            score += 4

    return score


def retrieve_conversation_context(
    user_id: Optional[str],
    query: str,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    检索当前用户相关历史对话上下文。

    本地轻量版：
    - user_id + order_id/product_id 结构化过滤；
    - 客服领域关键词打分；
    - 返回最相关历史消息和摘要；
    - 根据争议词判断风险等级。
    """
    if not user_id:
        return {
            "has_history": False,
            "summary": "未提供 user_id，无法检索用户历史对话。",
            "messages": [],
            "summaries": [],
            "risk_level": "unknown",
            "risk_reason": "missing_user_id",
        }

    summaries = query_summaries(user_id=user_id, product_id=product_id, order_id=order_id, limit=3)
    messages = query_messages(user_id=user_id, product_id=product_id, order_id=order_id, limit=30)

    scored_messages: List[Dict[str, Any]] = []
    for msg in messages:
        score = keyword_score(msg["content"], query)
        if score > 0:
            item = dict(msg)
            item["score"] = score
            scored_messages.append(item)

    scored_messages.sort(key=lambda x: (x["score"], x["created_at"]), reverse=True)
    top_messages = scored_messages[:top_k]

    history_text = "\n".join([m["content"] for m in top_messages])
    summary_text = "\n".join([s["summary"] + " " + (s.get("risk_tags") or "") for s in summaries])
    all_history_text = history_text + "\n" + summary_text

    current_has_dispute = any(kw in query for kw in DISPUTE_WORDS)
    query_refs_history = any(kw in query for kw in REFERENCE_HISTORY_WORDS)
    history_has_commitment = any(kw in all_history_text for kw in ["支持", "可以", "保证", "承诺"])
    history_marked_high_risk = any("高风险" in (s.get("risk_tags") or "") for s in summaries)

    if current_has_dispute and history_has_commitment:
        risk_level = "high"
        risk_reason = "当前问题包含明确争议表达，且历史对话存在客服承诺或商品属性答复"
    elif current_has_dispute and history_marked_high_risk:
        risk_level = "high"
        risk_reason = "当前问题包含明确争议表达，且历史摘要标记为高风险"
    elif query_refs_history and (top_messages or summaries):
        risk_level = "medium"
        risk_reason = "用户引用了历史咨询，已找到相关历史对话，可作为当前回复参考"
    elif top_messages or summaries:
        risk_level = "medium"
        risk_reason = "找到相关历史对话，可作为当前回复参考"
    else:
        risk_level = "low"
        risk_reason = "未找到明显相关历史对话"

    context_lines = []

    if summaries:
        context_lines.append("【历史会话摘要】")
        for s in summaries:
            context_lines.append(
                f"- 时间：{s['created_at']}；商品：{s.get('product_id') or '未知'}；摘要：{s['summary']}；风险标签：{s.get('risk_tags') or '无'}"
            )

    if top_messages:
        context_lines.append("【相关历史消息】")
        for m in top_messages:
            context_lines.append(
                f"- {m['created_at']} {m['role']}：{m['content']}（score={m['score']}）"
            )

    if not context_lines:
        context_lines.append("未检索到与当前问题明显相关的历史对话。")

    return {
        "has_history": bool(top_messages or summaries),
        "summary": "\n".join(context_lines),
        "messages": top_messages,
        "summaries": summaries,
        "risk_level": risk_level,
        "risk_reason": risk_reason,
    }
