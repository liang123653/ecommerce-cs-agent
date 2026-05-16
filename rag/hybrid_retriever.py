from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rag.platform_kb_retriever import retrieve_platform_kb


APPROVED_PLATFORM_CHUNKS = Path("data/platform_kb/approved_sop_cards.jsonl")


def _authority_rank(item: Dict[str, Any]) -> int:
    authority = item.get("authority", "")
    source_type = item.get("source_type", "")

    if authority == "official_public":
        return 4
    if authority == "official_api_doc":
        return 3
    if source_type == "merchant_policy":
        return 2
    if authority == "sample":
        return 1
    return 0


def retrieve_approved_platform_rules(
    query: str,
    scene: Optional[str],
    top_k: int = 2,
    candidate_k: int = 8,
    chunks_path: str | Path = APPROVED_PLATFORM_CHUNKS,
) -> List[Dict[str, Any]]:
    """
    检索人工审核通过的平台/商家知识 chunk。
    """
    path = Path(chunks_path)
    if not path.exists():
        return []

    candidates = retrieve_platform_kb(
        query=query,
        scene=scene,
        top_k=candidate_k,
        chunks_path=path,
        approved_only=True,
    )

    candidates = sorted(
        candidates,
        key=lambda x: (
            -_authority_rank(x),
            -float(x.get("score", 0)),
            x.get("chunk_id", ""),
        ),
    )

    return candidates[:top_k]


def format_platform_rules_for_prompt(
    chunks: List[Dict[str, Any]],
    max_chars_per_chunk: int = 420,
) -> str:
    """
    把平台规则 chunk 格式化成 prompt 文本。
    """
    if not chunks:
        return "无"

    lines = []

    for idx, item in enumerate(chunks, start=1):
        content = (item.get("customer_summary") or item.get("content", "")).strip().replace("\n", " ")
        if len(content) > max_chars_per_chunk:
            content = content[:max_chars_per_chunk] + "..."

        source_title = item.get("source_title", "")
        authority = item.get("authority", "")
        scene = item.get("scene", "")
        chunk_id = item.get("chunk_id", "")

        lines.append(
            f"{idx}. 来源：{source_title}；场景：{scene}；来源级别：{authority}；chunk_id：{chunk_id}\n"
            f"   内容：{content}"
        )

    return "\n".join(lines)


def format_platform_rule_facts_for_reference(
    chunks: List[Dict[str, Any]],
    max_chars_per_chunk: int = 360,
) -> str:
    """
    面向 reference_reply 的平台规则事实摘要。
    不暴露 chunk_id，避免最终回复泄漏内部检索细节。
    """
    if not chunks:
        return ""

    lines = []
    for idx, item in enumerate(chunks, start=1):
        content = (item.get("customer_summary") or item.get("content", "")).strip().replace("\n", " ")
        if len(content) > max_chars_per_chunk:
            content = content[:max_chars_per_chunk] + "..."

        source_title = item.get("source_title", "")
        lines.append(
            f"{idx}. 来源：{source_title}\n"
            f"   规则事实：{content}"
        )

    return "\n".join(lines)


def compose_reference_reply_with_platform_rules(
    reference_reply: str,
    platform_rule_chunks: List[Dict[str, Any]],
) -> str:
    """
    通用平台规则增强 reference_reply。

    目的：
    - 不为每个 scene 写专门 if；
    - 让 LLM 的“事实正确参考回复”真正吸收已审核平台规则；
    - 如果原 reference_reply 和平台规则冲突，以平台规则为准。
    """
    platform_facts = format_platform_rule_facts_for_reference(platform_rule_chunks)
    if not platform_facts:
        return reference_reply

    return f"""【平台官方规则事实，优先级最高】
{platform_facts}

【原参考回复，仅作话术参考】
{reference_reply}

【生成要求】
请优先回答用户当前问题。
如平台官方规则事实与原参考回复不一致，以平台官方规则事实为准。
不要展开用户没有询问的无关退换货资格、尺码、试穿等内容。
不要暴露 chunk_id、来源级别、检索细节或内部规则编号。"""



def _clean_rule_fact(content: str, max_chars: int = 460) -> str:
    """
    清洗平台规则文本，生成可直接给用户看的事实句。
    """
    text = (content or "").strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"第[一二三四五六七八九十百\d]+条\s*【[^】]+】", "", text)
    text = text.strip(" ；。")

    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    return text


def is_reply_grounded_by_platform_rules(
    reply: str,
    platform_rule_chunks: List[Dict[str, Any]],
    user_query: str = "",
) -> bool:
    """
    通用平台规则覆盖校验。

    不是判断回复好不好，只判断：
    如果已经命中了 official_public / official_api_doc 规则，
    最终回复是否至少覆盖了其中的关键业务词。
    """
    if not platform_rule_chunks:
        return True

    official_chunks = [
        x for x in platform_rule_chunks
        if x.get("authority") in {"official_public", "official_api_doc"}
    ]

    if not official_chunks:
        return True

    content = " ".join((x.get("content", "") or "") for x in official_chunks[:2])
    reply = reply or ""

    anchor_vocab = [
        "退回运费", "寄回运费", "退货运费", "运费", "邮费", "包邮", "未包邮", "附条件包邮",
        "买家承担", "商家承担", "双方另有约定", "七天无理由", "签收", "商品完好",
        "吊牌", "包装", "赠品", "无正当理由", "拒绝", "退货地址", "退款", "物流",
        "揽收", "发货", "超时", "投诉", "赔付", "发票",
    ]

    anchors = [w for w in anchor_vocab if w in content]

    # 如果 chunk 没有明显锚点，不做强校验，避免误伤。
    if not anchors:
        return True

    hit_count = sum(1 for w in anchors if w in reply)

    # 至少覆盖 2 个锚点；如果规则本身只有 1 个锚点，则覆盖 1 个即可。
    required = 1 if len(anchors) == 1 else 2
    return hit_count >= required


def _query_content_overlap_score(query: str, content: str) -> float:
    """
    通用 query-content 相关性分数。
    不依赖具体业务场景，避免继续堆 if/else。
    """
    q = re.sub(r"\s+", "", query or "")
    c = re.sub(r"\s+", "", content or "")

    if not q or not c:
        return 0.0

    score = 0.0

    # 1. 连续 2 字/3 字片段重合
    q_terms = set()
    for n in (2, 3, 4):
        for i in range(max(0, len(q) - n + 1)):
            q_terms.add(q[i:i+n])

    for t in q_terms:
        if t and t in c:
            score += len(t) * 0.5

    # 2. 完整短词命中加分，仍然是通用词面，不写具体场景分支
    for word in re.findall(r"[\u4e00-\u9fff]{2,}", q):
        if word in c:
            score += min(len(word), 6)

    return score


def build_platform_grounded_fallback_reply(
    user_query: str,
    platform_rule_chunks: List[Dict[str, Any]],
) -> str:
    """
    当 LLM 没有覆盖平台规则事实时，生成通用兜底回复。

    关键点：
    - 不按 scene 写分支；
    - 优先使用 official_public / official_api_doc；
    - 在候选 chunk 内按用户问题与规则内容的词面相关性再次排序；
    - 只取最相关的 1~2 条，避免回复过长和跑题。
    """
    official_chunks = [
        x for x in platform_rule_chunks
        if x.get("authority") in {"official_public", "official_api_doc"}
    ]

    candidates = official_chunks if official_chunks else platform_rule_chunks

    ranked = sorted(
        candidates,
        key=lambda x: (
            -_query_content_overlap_score(user_query, x.get("content", "")),
            -float(x.get("score", 0)),
            x.get("chunk_id", ""),
        ),
    )

    selected = ranked[:2]

    facts = []
    next_actions = []

    for item in selected:
        fact = item.get("customer_summary") or _clean_rule_fact(item.get("content", ""))
        if fact:
            facts.append(fact)

        action = item.get("next_action") or ""
        if action:
            next_actions.append(action)

    if not facts:
        return "您好，这个问题需要结合您的订单信息和商品页面说明进一步核实，我这边可以帮您继续查看。"

    fact_text = "；".join(facts)
    action_text = next_actions[0] if next_actions else "具体以您的订单情况和商品页面说明为准。"

    return (
        "您好，这边帮您说明一下："
        f"{fact_text}。"
        f"{action_text}"
    )
