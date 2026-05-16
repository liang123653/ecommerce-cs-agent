from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from rag.sop_card_retriever import (
    filter_sop_cards_for_prompt,
    retrieve_sop_cards,
)

from tools.fact_query import (
    after_sale_fact_query,
    express_policy_fact_query,
    logistics_fact_query,
    memory_fact_query,
    product_fact_query,
    promotion_fact_query,
    return_refund_fact_query,
    return_shipping_fact_query,
    shipping_fact_query,
)


DEFAULT_TAXONOMY = Path("data/platform_kb/taxonomy/customer_service_scene_taxonomy_v2.json")


def load_scene_taxonomy(path: str | Path = DEFAULT_TAXONOMY) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"scenes": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def card_identifier(card: Dict[str, Any]) -> str:
    return str(card.get("chunk_id") or card.get("card_id") or card.get("id") or "")


def serialize_sop_card(card: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": card_identifier(card),
        "scene": card.get("scene"),
        "score": card.get("score"),
        "base_score": card.get("base_score"),
        "source_type": card.get("source_type"),
        "authority": card.get("authority"),
        "source_batch": card.get("source_batch"),
        "customer_summary": card.get("customer_summary") or "",
        "next_action": card.get("next_action") or "",
    }


def normalize_scene_hints(
    scene_hint: Optional[Union[str, Sequence[str]]],
    taxonomy: Dict[str, Any],
) -> List[str]:
    scenes = taxonomy.get("scenes", {})

    if scene_hint is None:
        return []

    if isinstance(scene_hint, str):
        raw = [scene_hint]
    else:
        raw = [str(x) for x in scene_hint if str(x).strip()]

    normalized = []
    seen = set()

    for s in raw:
        if s in scenes and s not in seen:
            normalized.append(s)
            seen.add(s)

    return normalized


def required_contracts_for_scenes(
    scene_hints: Sequence[str],
    taxonomy: Dict[str, Any],
) -> List[str]:
    scenes = taxonomy.get("scenes", {})

    contracts: List[str] = []
    seen = set()

    for scene in scene_hints:
        cfg = scenes.get(scene, {})
        for c in cfg.get("required_fact_contracts", []) or []:
            if c not in seen:
                contracts.append(c)
                seen.add(c)

    return contracts


def risk_flags_for_scenes(
    scene_hints: Sequence[str],
    taxonomy: Dict[str, Any],
) -> List[str]:
    scenes = taxonomy.get("scenes", {})

    flags: List[str] = []
    seen = set()

    for scene in scene_hints:
        cfg = scenes.get(scene, {})
        for flag in cfg.get("risk_flags", []) or []:
            if flag not in seen:
                flags.append(flag)
                seen.add(flag)

    return flags


def knowledge_layers_for_scenes(
    scene_hints: Sequence[str],
    taxonomy: Dict[str, Any],
) -> List[str]:
    scenes = taxonomy.get("scenes", {})

    layers: List[str] = []
    seen = set()

    for scene in scene_hints:
        cfg = scenes.get(scene, {})
        for layer in cfg.get("knowledge_layers", []) or []:
            if layer not in seen:
                layers.append(layer)
                seen.add(layer)

    return layers


def _missing(name: str, required: Sequence[str]) -> Dict[str, Any]:
    return {
        "contract": name,
        "found": False,
        "skipped": True,
        "missing_required_args": list(required),
    }


def call_fact_contract(
    contract: str,
    *,
    order_id: Optional[str] = None,
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    user_id: Optional[str] = None,
    address_region: Optional[str] = None,
) -> Dict[str, Any]:
    """
    根据 contract 名称调用 fact tool。

    这里不做业务关键词判断，只执行 taxonomy 指定的动态事实查询。
    """
    if contract == "shipping_fact_query":
        if not order_id:
            return _missing(contract, ["order_id"])
        return shipping_fact_query(order_id)

    if contract == "logistics_fact_query":
        if not order_id:
            return _missing(contract, ["order_id"])
        return logistics_fact_query(order_id)

    if contract == "express_policy_fact_query":
        if not store_id:
            return _missing(contract, ["store_id"])
        return express_policy_fact_query(store_id, address_region=address_region)

    if contract == "return_refund_fact_query":
        if not order_id:
            return _missing(contract, ["order_id"])
        return return_refund_fact_query(order_id)

    if contract == "after_sale_fact_query":
        if not order_id:
            return _missing(contract, ["order_id"])
        return after_sale_fact_query(order_id)

    if contract == "return_shipping_fact_query":
        if not order_id:
            return _missing(contract, ["order_id"])
        return return_shipping_fact_query(order_id)

    if contract == "promotion_fact_query":
        if not store_id:
            return _missing(contract, ["store_id"])
        return promotion_fact_query(
            store_id,
            product_id=product_id,
            user_id=user_id,
        )

    if contract == "product_fact_query":
        if not product_id:
            return _missing(contract, ["product_id"])
        return product_fact_query(product_id)

    if contract == "memory_fact_query":
        if not user_id:
            return _missing(contract, ["user_id"])
        return memory_fact_query(
            user_id,
            order_id=order_id,
            product_id=product_id,
        )

    return {
        "contract": contract,
        "found": False,
        "skipped": True,
        "error": "unknown_contract",
    }


def derive_fact_risk_flags(facts: Dict[str, Any]) -> List[str]:
    """
    从事实结果中生成风险 flag。

    这不是业务分类路由，只是基于工具返回的结构化事实做安全提示。
    """
    flags: List[str] = []

    shipping = facts.get("shipping_fact_query") or {}
    if shipping.get("found"):
        if not shipping.get("has_shipped") and shipping.get("is_overdue"):
            flags.append("shipping_overdue_need_human")
        if shipping.get("has_shipped"):
            flags.append("already_shipped_do_not_answer_as_pre_ship")

    logistics = facts.get("logistics_fact_query") or {}
    if logistics.get("found"):
        if logistics.get("has_abnormal_tracking"):
            flags.append("abnormal_tracking_need_followup")
        if logistics.get("is_tracking_stalled"):
            flags.append("tracking_stalled_need_followup")

    express = facts.get("express_policy_fact_query") or {}
    if express.get("found"):
        if not express.get("can_guarantee_specific_carrier"):
            flags.append("do_not_guarantee_specific_carrier")

    ret = facts.get("return_refund_fact_query") or {}
    if ret.get("found"):
        if ret.get("return_address_available") is False:
            flags.append("do_not_fabricate_return_address")
        if ret.get("refund_arrival_status") == "not_refunded":
            flags.append("refund_not_arrived_do_not_claim_success")

    after_sale = facts.get("after_sale_fact_query") or {}
    if after_sale.get("found"):
        if after_sale.get("risk_need_human"):
            flags.append("after_sale_need_human")
        if after_sale.get("seller_response_status") == "refused":
            flags.append("seller_refusal_do_not_judge_violation_directly")

    return_shipping = facts.get("return_shipping_fact_query") or {}
    if return_shipping.get("found"):
        if return_shipping.get("compensation_arrival_status") == "not_arrived":
            flags.append("return_shipping_compensation_not_arrived")

    promotion = facts.get("promotion_fact_query") or {}
    if promotion.get("found"):
        if not promotion.get("manual_discount_allowed"):
            flags.append("manual_discount_not_allowed")

    memory = facts.get("memory_fact_query") or {}
    if memory.get("found"):
        if memory.get("has_pre_sale_commitment"):
            flags.append("has_pre_sale_commitment")
        if memory.get("conflict_with_product_fact"):
            flags.append("pre_sale_commitment_conflict_need_human")

    # 去重，保序
    out = []
    seen = set()
    for f in flags:
        if f not in seen:
            out.append(f)
            seen.add(f)

    return out


def retrieve_knowledge(
    query: str,
    *,
    scene_hint: Optional[Union[str, Sequence[str]]] = None,
    order_id: Optional[str] = None,
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    user_id: Optional[str] = None,
    address_region: Optional[str] = None,
    top_k: int = 5,
    prompt_top_k: int = 3,
    taxonomy_path: str | Path = DEFAULT_TAXONOMY,
) -> Dict[str, Any]:
    """
    统一知识检索骨架。

    注意：
    - 不做关键词路由；
    - scene_hint 来自上游候选路由或人工评测标签；
    - 根据 taxonomy 查需要的 fact contracts；
    - SOP 检索仍走原 RAG；
    - facts 用 tools/fact_query.py 的 mock tools。
    """
    taxonomy = load_scene_taxonomy(taxonomy_path)
    scene_hints = normalize_scene_hints(scene_hint, taxonomy)

    primary_scene = scene_hints[0] if scene_hints else None

    sop_cards = retrieve_sop_cards(
        query,
        scene=primary_scene,
        top_k=top_k,
    )

    prompt_sops = filter_sop_cards_for_prompt(
        query,
        sop_cards,
        policy_scene=primary_scene,
        top_k=prompt_top_k,
    )

    contracts = required_contracts_for_scenes(scene_hints, taxonomy)

    facts: Dict[str, Any] = {}
    missing_requirements: List[Dict[str, Any]] = []

    for contract in contracts:
        result = call_fact_contract(
            contract,
            order_id=order_id,
            store_id=store_id,
            product_id=product_id,
            user_id=user_id,
            address_region=address_region,
        )
        facts[contract] = result

        if result.get("skipped") or result.get("found") is False:
            if result.get("missing_required_args"):
                missing_requirements.append(result)

    taxonomy_risk_flags = risk_flags_for_scenes(scene_hints, taxonomy)
    fact_risk_flags = derive_fact_risk_flags(facts)

    risk_flags = []
    seen = set()
    for flag in taxonomy_risk_flags + fact_risk_flags:
        if flag not in seen:
            risk_flags.append(flag)
            seen.add(flag)

    return {
        "query": query,
        "scene_hints": scene_hints,
        "primary_scene": primary_scene,
        "knowledge_layers": knowledge_layers_for_scenes(scene_hints, taxonomy),
        "required_fact_contracts": contracts,
        "platform_sops": [serialize_sop_card(c) for c in sop_cards],
        "prompt_sops": [serialize_sop_card(c) for c in prompt_sops],
        "facts": facts,
        "risk_flags": risk_flags,
        "missing_requirements": missing_requirements,
        "debug": {
            "taxonomy_version": taxonomy.get("version"),
            "top_k": top_k,
            "prompt_top_k": prompt_top_k,
            "has_order_id": bool(order_id),
            "has_store_id": bool(store_id),
            "has_product_id": bool(product_id),
            "has_user_id": bool(user_id),
        },
    }


if __name__ == "__main__":
    demo = retrieve_knowledge(
        "订单什么时候发货？",
        scene_hint="shipping_policy",
        order_id="202604240001",
        store_id="demo_store_001",
        product_id="p001",
        user_id="u001",
    )
    print(json.dumps(demo, ensure_ascii=False, indent=2))
