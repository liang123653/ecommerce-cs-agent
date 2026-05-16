# -*- coding: utf-8 -*-
"""
Context-aware fallback v2 for controlled multi-turn customer service.

目标：
- 不做 scene 分类；
- 不调用旧 mainline retriever；
- 不扩业务关键词；
- 不承诺退款、赔偿、补发、发货、认责；
- 只在已有 history_context 时，给出保守的上下文承接回复。
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import re


EARLY_EXIT_STRATEGIES = {
    "LOW_INFO",
    "COMMON_SENSE",
    "SMALL_TALK",
    "PRODUCT_KNOWLEDGE",
}



def normalize_customer_reply(text: str) -> str:
    """
    清理中文客服回复里的多余空格和换行。
    例如：
    - '情况。 如果确认' -> '情况。如果确认'
    - '情况。\\n如果确认' -> '情况。如果确认'
    """
    if not text:
        return text

    # 统一不可见空白
    text = text.replace("\\r", " ").replace("\\n", " ").replace("\\t", " ")
    text = text.replace("\\u3000", " ")

    # 多个空白合并
    text = re.sub(r"\\s+", " ", text).strip()

    # 中文标点后面如果直接接中文，删除中间空格
    text = re.sub(r"([。！？；])\\s+(?=[\\u4e00-\\u9fff])", r"\\1", text)

    # 兜底处理常见拼接痕迹
    text = text.replace("。 如果确认", "。如果确认")
    text = text.replace("。 如果", "。如果")

    return text


def has_high_risk_summary_tag(history_context: Optional[Dict[str, Any]]) -> bool:
    """
    只读取历史摘要里已有的风险标签，不新增业务关键词规则。
    """
    if not history_context:
        return False

    for item in history_context.get("summaries") or []:
        risk_tags = item.get("risk_tags") or ""
        if "高风险" in risk_tags:
            return True

    return False


def should_use_context_aware_fallback(
    strategy: str,
    history_context: Optional[Dict[str, Any]],
) -> bool:
    """
    只对早退类策略启用 fallback。

    注意：
    - 不拦截 SOP_REQUIRED / FACT_REQUIRED / RISK_HANDOFF；
    - 不强制进入 answer_with_llm；
    - 没有历史时不启用。
    """
    if strategy not in EARLY_EXIT_STRATEGIES:
        return False

    if not history_context:
        return False

    if not history_context.get("has_history"):
        return False

    return True


def build_context_aware_fallback_reply(
    query: str,
    history_context: Dict[str, Any],
) -> str:
    """
    Context-aware fallback v2.

    v2 规则：
    - risk_level == high：严格核实 / 人工升级模板；
    - summary 里已有“高风险”：即使 risk_level 是 medium，也使用严格模板；
    - medium：上下文承接 + 补充凭证；
    - low / unknown：轻量承接，不承诺。
    """
    risk = history_context.get("risk_level")
    summary_marked_high = has_high_risk_summary_tag(history_context)

    if risk == "high" or summary_marked_high:
        return (
            "抱歉给您带来困扰，这种情况我先帮您按售后核实问题处理。"
            "我会结合前面的沟通记录、订单信息、商品页面说明和您收到的实物情况一起核实。"
            "麻烦您发一下订单号、商品页面截图和实物照片，我这边先帮您整理情况。"
            "如果确认售前答复、页面说明或实际商品存在不一致，我会帮您转人工或售后专员继续处理。"
        )

    if risk == "medium":
        return (
            "我明白，您这个问题是接着前面的沟通继续确认。"
            "我会结合之前的咨询记录一起看，避免让您重复说明。"
            "麻烦您补充一下订单号、商品链接或相关截图，我这边继续帮您核实。"
        )

    return (
        "我理解您是在接着前面的问题继续确认。"
        "我会结合前面的沟通记录帮您看一下，但具体结果还需要以订单、商品页面或实际状态为准。"
        "麻烦您补充一下订单号或商品信息，我再帮您核实。"
    )


def build_context_fallback_result(
    query: str,
    strategy: str,
    original_reply: str,
    history_context: Dict[str, Any],
    product_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    统一返回 answer_with_strategy 风格的结果。
    """
    reply = build_context_aware_fallback_reply(query, history_context)
    reply = normalize_customer_reply(reply)

    return {
        "strategy": strategy,
        "mainline_used": False,
        "context_fallback_used": True,
        "context_fallback_version": "v2",
        "scene": None,
        "policy_file": None,
        "order_id": None,
        "product_id": product_id,
        "reply": reply,
        "original_early_exit_reply": original_reply,
        "history_context": history_context,
        "history_risk_level": history_context.get("risk_level"),
        "history_risk_reason": history_context.get("risk_reason"),
    }
