from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SOP_CARDS = Path("data/platform_kb/approved_sop_cards.jsonl")


def load_sop_cards(path: str | Path = DEFAULT_SOP_CARDS) -> List[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def build_card_search_text(card: Dict[str, Any]) -> str:
    """
    SOP Card 检索文本。

    注意：
    - 优先检索客服化摘要和审核字段；
    - 官方原文 content 只是补充；
    - 不在代码里写具体业务关键词。
    """
    parts = []

    for key in [
        "customer_summary",
        "next_action",
        "content",
    ]:
        value = card.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value)

    for key in [
        "user_intents",
        "conditions",
        "need_human_conditions",
    ]:
        value = card.get(key)
        if isinstance(value, list):
            parts.extend(str(x) for x in value if str(x).strip())

    return "\n".join(parts)


def char_ngram_score(query: str, text: str) -> float:
    """
    通用字符 ngram 检索分数。
    不写业务关键词，避免规则堆叠。
    """
    q = normalize_text(query)
    t = normalize_text(text)

    if not q or not t:
        return 0.0

    score = 0.0

    for n in (2, 3, 4):
        seen = set()
        for i in range(max(0, len(q) - n + 1)):
            gram = q[i:i + n]
            if gram and gram not in seen:
                seen.add(gram)
                if gram in t:
                    score += n

    # 完整 query 子串命中，额外加分
    if len(q) >= 4 and q in t:
        score += 8.0

    return score


def authority_boost(card: Dict[str, Any]) -> float:
    authority = card.get("authority", "")
    source_type = card.get("source_type", "")

    if authority == "official_public":
        return 3.0
    if authority == "official_api_doc":
        return 2.0
    if source_type == "merchant_policy":
        return 1.0
    if authority == "sample":
        return -1.0

    return 0.0




# Phase 13H-B:
# 官方平台规则卡不能仅靠 authority_boost 进入候选。
# 先要求 query 和卡片字段有真实文本匹配，再允许加权排序。
OFFICIAL_PLATFORM_MIN_BASE_SCORE = float(
    os.getenv("SOP_OFFICIAL_PLATFORM_MIN_BASE_SCORE", "8")
)


def is_weak_sop_query(query: str) -> bool:
    """
    稳定硬过滤：只过滤明显不适合进入 SOP 检索的短寒暄、确认、纯占位内容。
    这里不做业务分类，不枚举业务词。
    """
    q = normalize_text(query).lower()
    q = re.sub(r"\[long_number\]|\[number\]|\[phone\]", "", q)
    q = re.sub(r"[0-9]+", "", q)
    q = re.sub(r"[^\u4e00-\u9fffA-Za-z]+", "", q)

    if not q:
        return True

    if len(q) <= 2:
        return True

    weak_phrases = {
        "ok",
        "好的",
        "好吧",
        "好的谢谢",
        "谢谢",
        "谢谢啦",
        "谢了",
        "谢",
        "嗯嗯",
        "恩恩",
        "对的",
        "对的亲",
        "是的",
        "真的吗",
        "知道了",
        "辛苦了",
    }

    return q in weak_phrases


def is_phase13_platform_card(card: Dict[str, Any]) -> bool:
    """
    识别 Phase13 新增官方平台规则卡。
    用于低分门控和同分排序保护，不改变卡片内容。
    """
    chunk_id = str(card.get("chunk_id") or card.get("card_id") or card.get("id") or "")
    source_type = card.get("source_type", "")
    authority = card.get("authority", "")
    source_batch = str(card.get("source_batch", ""))

    if source_type != "platform_rule":
        return False

    if "phase13" in source_batch:
        return True

    return chunk_id.startswith("taobao_") and authority in {
        "official_public",
        "official_api_doc",
    }


SENSITIVE_PHASE13_PROMPT_IDS = {
    "taobao_delivery_false_shipment_0001",
    "taobao_breach_promise_gift_0001",
    "taobao_breach_promise_discount_difference_0001",
    "taobao_dispute_address_change_failed_0001",
    "taobao_unreasonable_refusal_after_sale_0001",
}

SENSITIVE_PHASE13_PROMPT_MIN_SCORE = float(
    os.getenv("SOP_SENSITIVE_PHASE13_PROMPT_MIN_SCORE", "20")
)

SENSITIVE_PHASE13_PROMPT_MIN_MARGIN = float(
    os.getenv("SOP_SENSITIVE_PHASE13_PROMPT_MIN_MARGIN", "6")
)


def card_identifier(card: Dict[str, Any]) -> str:
    return str(card.get("chunk_id") or card.get("card_id") or card.get("id") or "")


DISCOUNT_DIFFERENCE_CARD_ID = "taobao_breach_promise_discount_difference_0001"


def is_discount_difference_prompt_eligible(query: str) -> bool:
    """
    差价/价保承诺未履约卡的 prompt 资格门控。

    只用于高风险卡 taobao_breach_promise_discount_difference_0001。
    不是全局业务分类，也不做场景路由；只判断这张卡是否有足够证据进入 prompt。
    """
    q = normalize_text(query)

    if not q:
        return False

    # 明确否定：用户说不用/不需要/无需补差价时，不能进入“差价承诺未履约”。
    neg_pattern = r"(不用|不需要|无需|不要|先不|暂不).{0,6}(补差价|退差价|退差|价保|价格差额|差价)"
    if re.search(neg_pattern, q):
        return False

    # 必须有明确的差价/价保/价格差额证据。
    price_diff_pattern = r"(补差价|退差价|退差|价保|价格差额|差价|降价|买贵|贵了|便宜了)"
    has_price_diff_evidence = bool(re.search(price_diff_pattern, q))

    if not has_price_diff_evidence:
        return False

    # 必须有未履约、未到账、金额不对、拒绝处理等结果证据。
    breach_pattern = r"(没退|没补|未退|未补|没到|未到|不到账|未到账|金额不对|不处理|拒绝|一直没|还没|怎么没|没有退|没有补)"
    has_breach_evidence = bool(re.search(breach_pattern, q))

    if not has_breach_evidence:
        return False

    return True


def filter_sop_cards_for_prompt(
    query: str,
    cards: List[Dict[str, Any]],
    policy_scene: Optional[str] = None,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Phase 13H-C prompt eligibility gate.

    目的：
    - 允许 SOP Card 被检索；
    - 但高风险 Phase13 平台规则卡必须满足更严格条件才进入 prompt；
    - 避免“普通优惠券/赠品咨询/物流担忧/寒暄短句”把强平台规则塞进生成上下文。

    这里不做业务分类，不新增业务词表，只基于：
    - query 是否弱；
    - 卡片是否 Phase13 官方平台卡；
    - 是否与主 policy scene 一致；
    - 分数是否足够高；
    - 是否明显领先旧卡/普通卡。
    """
    if not cards:
        return []

    if is_weak_sop_query(query):
        return []

    kept = []
    scores = []
    for c in cards:
        try:
            scores.append(float(c.get("score", 0)))
        except Exception:
            scores.append(0.0)

    for rank, card in enumerate(cards):
        cid = card_identifier(card)
        card_scene = card.get("scene", "")
        score = scores[rank]

        if cid == DISCOUNT_DIFFERENCE_CARD_ID and not is_discount_difference_prompt_eligible(query):
            continue

        # 非 Phase13 官方平台卡沿用原逻辑
        if not is_phase13_platform_card(card):
            kept.append(card)
            continue

        # Phase13 官方平台卡必须和主 policy scene 一致，避免跨场景强规则进 prompt
        if policy_scene and card_scene and card_scene != policy_scene:
            continue

        # 非敏感 Phase13 卡可以进入，但仍受检索阶段低分门控约束
        if cid not in SENSITIVE_PHASE13_PROMPT_IDS:
            kept.append(card)
            continue

        # 敏感卡必须是 top1；top2/top3 只保留候选，不进入 prompt
        if rank != 0:
            continue

        # 敏感卡必须达到更高分数
        if score < SENSITIVE_PHASE13_PROMPT_MIN_SCORE:
            continue

        # 敏感卡必须明显领先最佳非 Phase13 卡，否则说明只是相近候选，不进 prompt
        best_non_phase13 = 0.0
        for j, other in enumerate(cards):
            if not is_phase13_platform_card(other):
                best_non_phase13 = max(best_non_phase13, scores[j])

        if best_non_phase13 and score - best_non_phase13 < SENSITIVE_PHASE13_PROMPT_MIN_MARGIN:
            continue

        kept.append(card)

    if top_k is not None:
        return kept[:top_k]

    return kept


def retrieve_sop_cards(
    query: str,
    scene: Optional[str] = None,
    top_k: int = 3,
    cards_path: str | Path = DEFAULT_SOP_CARDS,
    approved_only: bool = True,
) -> List[Dict[str, Any]]:
    """
    检索 SOP Card。

    只做通用检索：
    - scene 过滤；
    - approved 过滤；
    - customer_summary / user_intents / conditions 等字段检索；
    - authority boost。
    """
    rows = load_sop_cards(cards_path)

    if is_weak_sop_query(query):
        return []

    scored = []
    for card in rows:
        if approved_only and card.get("status") != "approved":
            continue

        if scene and card.get("scene") != scene:
            continue

        search_text = build_card_search_text(card)
        intent_text = "\n".join(card.get("user_intents") or [])

        base_score = (
            char_ngram_score(query, search_text)
            + 2.0 * char_ngram_score(query, intent_text)
        )

        # 不能让 authority_boost 把完全无文本匹配的官方卡抬进候选。
        if base_score <= 0:
            continue

        # Phase13 官方平台规则卡属于高权威但高风险候选：
        # 必须先有足够文本匹配，才允许进入最终 topK。
        if is_phase13_platform_card(card) and base_score < OFFICIAL_PLATFORM_MIN_BASE_SCORE:
            continue

        boost = authority_boost(card)
        final_score = base_score + boost

        if final_score <= 0:
            continue

        item = dict(card)
        item["score"] = final_score
        item["base_score"] = base_score
        item["authority_boost"] = boost
        scored.append(item)

    return sorted(
        scored,
        key=lambda x: (
            -float(x.get("score", 0)),
            1 if is_phase13_platform_card(x) else 0,
            -float(x.get("base_score", 0)),
            x.get("chunk_id", ""),
        ),
    )[:top_k]


def format_sop_cards_for_prompt(cards: List[Dict[str, Any]]) -> str:
    """
    面向 prompt 的 SOP Card 展示。
    不把官方原文作为主要回复材料。
    """
    if not cards:
        return "无"

    lines = []

    for idx, card in enumerate(cards, start=1):
        summary = card.get("customer_summary") or card.get("content", "")
        conditions = card.get("conditions") or []
        need_human = card.get("need_human_conditions") or []
        do_not_say = card.get("do_not_say") or []
        next_action = card.get("next_action") or ""

        lines.append(f"{idx}. 客服化规则摘要：{summary}")

        if conditions:
            lines.append("   适用条件：" + "；".join(conditions))

        if need_human:
            lines.append("   需要人工/进一步核实：" + "；".join(need_human))

        if do_not_say:
            lines.append("   禁止承诺：" + "；".join(do_not_say))

        if next_action:
            lines.append("   建议下一步：" + next_action)

    return "\n".join(lines)


def _clean_customer_sentence(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip("。；;，, ")


def _clean_next_action(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip("。；;，, ")

    if not text:
        return "具体可以结合您的订单情况进一步确认。"

    if text.startswith("让用户"):
        text = text.replace("让用户", "您可以", 1)
    elif text.startswith("引导用户"):
        text = text.replace("引导用户", "您可以", 1)
    elif text.startswith("结合"):
        text = "可以" + text

    return text + "。"


def build_sop_card_fallback_reply(cards: List[Dict[str, Any]]) -> str:
    """
    通用 SOP Card 兜底回复。

    不使用官方原文，不念规则条款；
    只使用 customer_summary + next_action。
    """
    if not cards:
        return "您好，这个问题需要结合订单和商品情况进一步核实，我这边可以继续帮您查看。"

    card = cards[0]

    summary = _clean_customer_sentence(card.get("customer_summary") or "")
    next_action = _clean_next_action(card.get("next_action") or "")

    if not summary:
        summary = "这个问题需要结合订单、商品页面说明和实际情况确认"

    return f"您好，这边帮您说明一下：{summary}。{next_action}"
