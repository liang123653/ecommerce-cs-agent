from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.multi_scene_router import normalize_text, route_with_multiscene_router


def _extract_current_user_turn(route_input: str) -> str:
    """
    只提取最后一条用户消息，避免 rerank 被历史上下文污染。
    """
    last = ""
    for line in (route_input or "").splitlines():
        line = line.strip()
        if line.startswith("用户："):
            last = line.split("用户：", 1)[1].strip()

    if not last:
        last = route_input or ""

    return normalize_text(last)



SCENE_TO_FILE = {
    "shipping_policy": "shipping_policy.md",
    "logistics_policy": "logistics_policy.md",
    "express_policy": "express_policy.md",
    "order_modify_policy": "order_modify_policy.md",
    "promotion_policy": "promotion_policy.md",
    "coupon_policy": "coupon_policy.md",
    "shipping_fee_policy": "shipping_fee_policy.md",
    "gift_policy": "gift_policy.md",
    "product_qa_policy": "product_qa_policy.md",
    "stock_policy": "stock_policy.md",
    "bulk_purchase_policy": "bulk_purchase_policy.md",
    "missing_package_policy": "missing_package_policy.md",
    "refund_policy": "refund_policy.md",
    "return_exchange": "return_exchange.md",
    "price_protection": "price_protection.md",
    "invoice_policy": "invoice_policy.md",
    "quality_issue": "quality_issue.md",
    "description_mismatch": "description_mismatch_policy.md",
    "complaint_policy": "complaint_policy.md",
}


def _candidate(result: Dict[str, Any], scene: str) -> Optional[Dict[str, Any]]:
    for item in result.get("candidate_scenes", []) or []:
        if item.get("scene") == scene:
            return item
    return None


def _promote(result: Dict[str, Any], scene: str, reason: str, bonus: float = 0.5) -> Dict[str, Any]:
    """
    将某个候选场景提升为 Top1。
    如果候选中没有该 scene，则注入一个低分候选，避免因为 schema 漏召回导致强规则完全无效。
    """
    result = deepcopy(result)
    candidates: List[Dict[str, Any]] = result.get("candidate_scenes", []) or []
    target = None

    for item in candidates:
        if item.get("scene") == scene:
            target = item
            break

    if target is None:
        target = {
            "scene": scene,
            "file_name": SCENE_TO_FILE.get(scene, f"{scene}.md"),
            "score": max(float(result.get("score") or 0) + bonus, bonus),
            "priority": 0,
            "hits": [],
            "negative_hits": [],
            "description": "phase8.2 rerank injected candidate",
        }
        candidates.append(target)

    top_score = max([float(x.get("score") or 0) for x in candidates] + [0])
    target["score"] = round(max(float(target.get("score") or 0), top_score + bonus), 4)
    target["rerank_promoted"] = True
    target["rerank_reason"] = reason

    candidates.sort(key=lambda x: float(x.get("score") or 0), reverse=True)

    result["scene"] = scene
    result["file_name"] = SCENE_TO_FILE.get(scene, f"{scene}.md")
    result["score"] = target["score"]
    result["hits"] = target.get("hits", [])
    result["router_reason"] = reason
    result["router_source"] = "phase8_2_multiscene_router_with_rerank"
    result["candidate_scenes"] = candidates

    return result


def rerank_phase8_result(route_input: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 8.2 rerank 层。

    原则：
    - 不再把大量业务判断写到主 router；
    - 只处理少数高确定性“主意图优先”规则；
    - 规则触发后只调整 Top1，不改变候选召回逻辑。
    """
    t = _extract_current_user_turn(route_input)

    # 1. 描述/承诺不一致属于高风险优先：
    #    “不是说2份送一包怎么没送啊”虽然包含赠品词，但核心是承诺不一致。
    if re.search(r"(不是说|说了|说好|页面写|客服说|你们说).*(没送|没有送|少送|不送|送一包|不一样|不符|假的|结果)", t):
        return _promote(result, "description_mismatch", "phase8_2_rerank_description_mismatch_priority", bonus=1.2)

    # 2. 运费核心词优先于“改一下”这种订单修改泛词。
    if re.search(r"(运费|邮费|快递费).*(改|减|免|补|多少)|改.*(运费|邮费|快递费)", t):
        return _promote(result, "shipping_fee_policy", "phase8_2_rerank_shipping_fee_core_intent", bonus=1.0)

    # 3. 当前轮明确发货时效，优先 shipping。
    if re.search(r"(还不发货|什么时候.*发|多久发货|几天发货|今天.*发货|今天能发|明天.*发货|能发货吗|可以发吗|尽快发货|加急发货)", t):
        return _promote(result, "shipping_policy", "phase8_2_rerank_shipping_current_intent", bonus=0.9)

    # 4. 当前轮明确物流慢/查快递，优先 logistics。
    if re.search(r"(怎么那么慢|查快递|快递到了|通知收件人|没音讯|没动静|物流没动|一直不动|到哪了)", t):
        return _promote(result, "logistics_policy", "phase8_2_rerank_logistics_current_intent", bonus=0.9)

    return result


def route_with_phase8_2_router(route_query: str, top_k: int = 5) -> Dict[str, Any]:
    base = route_with_multiscene_router(route_query, top_k=top_k)
    reranked = rerank_phase8_result(route_query, base)

    # rerank 后保留 top_k 个候选，避免报告太长
    if reranked.get("candidate_scenes"):
        reranked["candidate_scenes"] = reranked["candidate_scenes"][:top_k]

    return reranked
