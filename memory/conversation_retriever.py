# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List
import re

from memory.conversation_store import query_messages, query_summaries


def normalize_text(text: str) -> str:
    """
    通用文本归一化：
    - 去掉空白；
    - 不做业务词表匹配；
    - 不做商品属性枚举。
    """
    return re.sub(r"\s+", "", text or "")


def char_ngram_score(query: str, text: str) -> float:
    """
    通用字符 n-gram 相似度。

    设计原则：
    - 不写商品词表；
    - 不写售后/物流/退款业务词表；
    - 不根据某个具体商品属性做规则判断；
    - 只看当前 query 和历史消息在字面片段上的通用重合度。
    """
    q = normalize_text(query)
    t = normalize_text(text)

    if not q or not t:
        return 0.0

    score = 0.0

    for n in (2, 3, 4):
        grams = set()
        for i in range(max(0, len(q) - n + 1)):
            gram = q[i:i + n]
            if gram:
                grams.add(gram)

        for gram in grams:
            if gram in t:
                score += float(n)

    # 完整 query 子串命中，额外加分。
    if len(q) >= 4 and q in t:
        score += 8.0

    return score


def has_history_reference(query: str) -> bool:
    """
    稳定历史引用 hint。

    这里只判断用户是否在引用历史会话，
    不做业务分类，不判断售后/退款/物流/商品属性。
    """
    q = normalize_text(query)

    # 这是少量稳定会话指代表达，不是业务词表。
    hints = ("之前", "上次", "刚才", "当时", "你们说", "客服说", "问过")
    return any(h in q for h in hints)


def _summary_marked_high_risk(summary: Dict[str, Any]) -> bool:
    risk_tags = str(summary.get("risk_tags") or "")
    risk_level = str(summary.get("risk_level") or "")
    return "高风险" in risk_tags or risk_level.lower() == "high"


def retrieve_conversation_context(
    user_id: Optional[str],
    query: str,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    检索当前用户相关历史对话上下文。

    当前版本：
    - user_id + order_id/product_id 结构化过滤；
    - 用通用 char n-gram 做历史消息相关性排序；
    - 风险等级主要来自 summary/risk_tags；
    - 不再使用商品属性词表、争议词表、业务关键词词表。

    注意：
    - memory 只表示历史说过什么；
    - memory 不是商品事实源，也不是订单事实源；
    - 商品/订单/售后事实仍以业务库、工具查询和官方 SOP 为准。
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

    raw_summaries = query_summaries(
        user_id=user_id,
        product_id=product_id,
        order_id=order_id,
        limit=5,
    )

    messages = query_messages(
        user_id=user_id,
        product_id=product_id,
        order_id=order_id,
        limit=30,
    )

    # summary 也需要做 query 相关性过滤。
    # 否则只按 user_id 查询时，同一用户的其他商品高风险摘要会污染当前问题。
    scoped_history = bool(product_id or order_id)
    scored_summaries: List[Dict[str, Any]] = []

    for s in raw_summaries:
        summary_text = " ".join([
            str(s.get("summary") or ""),
            str(s.get("risk_tags") or ""),
            str(s.get("product_id") or ""),
            str(s.get("order_id") or ""),
        ])
        score = char_ngram_score(query, summary_text)

        # 如果已经有 product_id/order_id 精确过滤，可以保留该作用域下的摘要；
        # 如果只是 user_id 级别兜底，则必须和当前 query 有文本相关性。
        if scoped_history or score > 0:
            item = dict(s)
            item["score"] = score
            scored_summaries.append(item)

    scored_summaries.sort(
        key=lambda x: (
            float(x.get("score", 0)),
            str(x.get("created_at", "")),
        ),
        reverse=True,
    )

    summaries = scored_summaries[:3]

    scored_messages: List[Dict[str, Any]] = []

    for msg in messages:
        content = msg.get("content") or msg.get("message") or msg.get("text") or ""
        score = char_ngram_score(query, content)

        if score > 0:
            item = dict(msg)
            item["score"] = score
            scored_messages.append(item)

    scored_messages.sort(
        key=lambda x: (
            float(x.get("score", 0)),
            str(x.get("created_at", "")),
        ),
        reverse=True,
    )

    top_messages = scored_messages[:top_k]

    # 高风险只能来自“当前作用域内”或“与 query 明显相关”的摘要。
    # 避免 user_id 级别兜底时，被其他商品/其他订单的高风险摘要误伤。
    history_marked_high_risk = any(
        _summary_marked_high_risk(s)
        and (scoped_history or float(s.get("score", 0)) >= 4.0)
        for s in summaries
    )
    query_refs_history = has_history_reference(query)

    if history_marked_high_risk:
        risk_level = "high"
        risk_reason = "历史摘要存在高风险标签，需要谨慎承接历史答复"
    elif query_refs_history and (top_messages or summaries):
        risk_level = "medium"
        risk_reason = "用户引用了历史咨询，已找到相关历史对话"
    elif top_messages or summaries:
        risk_level = "medium"
        risk_reason = "找到相关历史对话，可作为上下文参考"
    else:
        risk_level = "low"
        risk_reason = "未找到明显相关历史对话"

    context_lines: List[str] = []

    if summaries:
        context_lines.append("【历史会话摘要】")
        for s in summaries:
            context_lines.append(
                f"- 时间：{s.get('created_at')}; "
                f"商品：{s.get('product_id') or '未知'}; "
                f"摘要：{s.get('summary') or ''}; "
                f"风险标签：{s.get('risk_tags') or '无'}"
            )

    if top_messages:
        context_lines.append("【相关历史消息】")
        for m in top_messages:
            content = m.get("content") or m.get("message") or m.get("text") or ""
            context_lines.append(
                f"- {m.get('created_at')} {m.get('role')}："
                f"{content}（score={m.get('score')}）"
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
