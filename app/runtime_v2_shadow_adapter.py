# -*- coding: utf-8 -*-
"""
Runtime v2 Shadow Adapter

作用：
- 不修改 answer_with_llm
- 不替换 retrieve_policy_auto
- 不覆盖 final reply
- 只生成 shadow trace，供后续 Evaluation Harness 使用

Phase19-E:
- 复用 app/current_turn_router_v2.py::detect_current_turn_scene_v2
- 支持 route_query，用于传入 first_user_query + last_user_query
- 不再重新实现低信息短句规则
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


AFTER_SALES_BIAS_SCENES = {"refund_policy", "return_exchange"}


def _safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs), None
    except Exception as exc:
        return None, repr(exc)


def _extract_scene(result: Optional[dict]) -> Optional[str]:
    if not isinstance(result, dict):
        return None
    scene = result.get("scene")
    if scene and scene != "unknown":
        return scene
    return None


def _extract_phase8_scenes(route: Optional[dict]) -> List[str]:
    if not isinstance(route, dict):
        return []

    scenes: List[str] = []

    scene = route.get("scene")
    if scene and scene != "unknown":
        scenes.append(scene)

    for item in route.get("candidate_scenes") or []:
        if isinstance(item, str):
            s = item
        elif isinstance(item, dict):
            s = item.get("scene")
        else:
            s = None

        if s and s != "unknown" and s not in scenes:
            scenes.append(s)

    return scenes


def build_route_candidate_trace(
    query: str,
    *,
    route_query: Optional[str] = None,
) -> Dict[str, Any]:
    """
    生成 route shadow trace。

    query:
        当前用户 query，一般是 last_user_query。

    route_query:
        用于路由的上下文 query。
        例如：
            用户：first_user_query
            用户：last_user_query

    注意：
    - current_policy 仍然只作为旧 runtime debug；
    - current_turn_router_v2 / phase8 作为 shadow candidate provider；
    - 这里只观察，不覆盖。
    """
    effective_route_query = route_query or query

    current_policy = None
    current_error = None

    phase8_route = None
    phase8_error = None

    current_turn_v2 = None
    current_turn_v2_error = None

    # 旧 runtime policy，只做 debug。这里保留 query，不用 route_query，方便观察旧 runtime 对当前轮的偏置。
    try:
        from app.pipeline_llm import retrieve_policy_auto

        current_policy, current_error = _safe_call(retrieve_policy_auto, query)
    except Exception as exc:
        current_error = repr(exc)

    # Phase8 multi-scene router，用 route_query。
    try:
        from app.phase8_reranker import route_with_phase8_2_router

        phase8_route, phase8_error = _safe_call(
            route_with_phase8_2_router,
            effective_route_query,
            top_k=5,
        )
    except Exception as exc:
        phase8_error = repr(exc)

    # 复用已有 current_turn_router_v2，不新写低信息规则。
    try:
        from app.current_turn_router_v2 import detect_current_turn_scene_v2

        current_turn_v2, current_turn_v2_error = _safe_call(
            detect_current_turn_scene_v2,
            effective_route_query,
        )
    except Exception as exc:
        current_turn_v2_error = repr(exc)

    current_scene = None
    if isinstance(current_policy, dict):
        current_scene = current_policy.get("scene")

    phase8_scenes = _extract_phase8_scenes(phase8_route)
    phase8_primary = phase8_scenes[0] if phase8_scenes else None

    current_turn_v2_scene = _extract_scene(current_turn_v2)

    candidate_scenes: List[str] = []

    # Phase19-F arbitration:
    # 1. Phase8 当前在 50 条 smoke 上效果最好，优先作为 primary；
    # 2. current_turn_router_v2 只作为 context rescue provider；
    # 3. current_policy 如果是 after-sales 偏置，不进入 knowledge_router；
    # 4. current_policy 只保留 debug。
    for s in phase8_scenes:
        if s not in candidate_scenes:
            candidate_scenes.append(s)

    if current_turn_v2_scene and current_turn_v2_scene not in candidate_scenes:
        candidate_scenes.append(current_turn_v2_scene)

    if (
        current_scene
        and current_scene not in AFTER_SALES_BIAS_SCENES
        and current_scene != "unknown"
        and current_scene not in candidate_scenes
    ):
        candidate_scenes.append(current_scene)

    trusted_primary = candidate_scenes[0] if candidate_scenes else None

    low_confidence_current_only = bool(
        not trusted_primary
        and current_scene in AFTER_SALES_BIAS_SCENES
    )

    scene_conflict = bool(
        current_scene
        and trusted_primary
        and current_scene != trusted_primary
    )

    provider_disagreement = bool(
        current_turn_v2_scene
        and phase8_primary
        and current_turn_v2_scene != phase8_primary
    )

    return {
        "query": query,
        "effective_route_query": effective_route_query,
        "current_policy": {
            "scene": current_scene,
            "file_name": current_policy.get("file_name") if isinstance(current_policy, dict) else None,
            "retriever": current_policy.get("retriever") if isinstance(current_policy, dict) else None,
            "error": current_error,
        },
        "phase8_route": {
            "scene": phase8_route.get("scene") if isinstance(phase8_route, dict) else None,
            "candidate_scenes": phase8_scenes,
            "raw_router_reason": phase8_route.get("router_reason") if isinstance(phase8_route, dict) else None,
            "error": phase8_error,
        },
        "current_turn_v2": {
            "scene": current_turn_v2_scene,
            "raw_scene": current_turn_v2.get("scene") if isinstance(current_turn_v2, dict) else None,
            "file_name": current_turn_v2.get("file_name") if isinstance(current_turn_v2, dict) else None,
            "score": current_turn_v2.get("score") if isinstance(current_turn_v2, dict) else None,
            "router_reason": current_turn_v2.get("router_reason") if isinstance(current_turn_v2, dict) else None,
            "router_scope": current_turn_v2.get("router_scope") if isinstance(current_turn_v2, dict) else None,
            "error": current_turn_v2_error,
        },
        "candidate_scenes": candidate_scenes,
        "arbitration": {
            "trusted_primary": trusted_primary,
            "current_turn_v2_primary": current_turn_v2_scene,
            "phase8_primary": phase8_primary,
            "scene_conflict_with_current_policy": scene_conflict,
            "provider_disagreement": provider_disagreement,
            "low_confidence_current_only": low_confidence_current_only,
            "policy": "prefer_phase8_then_current_turn_v2_rescue; keep_current_policy_debug_only_when_after_sales_biased",
        },
        "shadow_only": True,
        "allow_replace_policy_scene": False,
        "allow_override_final_reply": False,
    }


def build_runtime_v2_shadow_trace(
    query: str,
    *,
    route_query: Optional[str] = None,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
    store_id: Optional[str] = None,
    address_region: Optional[str] = None,
    top_k: int = 5,
    prompt_top_k: int = 3,
) -> Dict[str, Any]:
    """
    生成 runtime_v2 shadow trace。

    输出：
    - route_trace
    - knowledge_trace
    - missing_requirements
    - risk_flags

    注意：
    - 不进入 prompt
    - 不替换当前 policy scene
    - 不覆盖 final reply
    """
    route_trace = build_route_candidate_trace(query, route_query=route_query)
    candidate_scenes = route_trace.get("candidate_scenes") or []
    effective_route_query = route_trace.get("effective_route_query") or query

    knowledge_trace: Dict[str, Any]

    if not candidate_scenes:
        knowledge_trace = {
            "query": effective_route_query,
            "scene_hints": [],
            "primary_scene": None,
            "knowledge_layers": [],
            "required_fact_contracts": [],
            "platform_sops": [],
            "prompt_sops": [],
            "facts": {},
            "risk_flags": [],
            "missing_requirements": [],
            "debug": {
                "blocked_by_adapter": True,
                "blocked_reason": "no_reliable_scene_hint",
            },
            "error": None,
        }

        return {
            "query": query,
            "route_query": effective_route_query,
            "route_trace": route_trace,
            "knowledge_trace": knowledge_trace,
            "shadow_decision": {
                "shadow_only": True,
                "allow_enter_prompt": False,
                "allow_replace_policy_scene": False,
                "allow_override_final_reply": False,
                "reason": "blocked_no_reliable_scene_hint",
            },
        }

    try:
        from rag.knowledge_router import retrieve_knowledge

        knowledge_trace, err = _safe_call(
            retrieve_knowledge,
            effective_route_query,
            scene_hint=candidate_scenes,
            order_id=order_id,
            store_id=store_id,
            product_id=product_id,
            user_id=user_id,
            address_region=address_region,
            top_k=top_k,
            prompt_top_k=prompt_top_k,
        )

        if not isinstance(knowledge_trace, dict):
            knowledge_trace = {}

        knowledge_trace["error"] = err

    except Exception as exc:
        knowledge_trace = {
            "error": repr(exc),
            "scene_hints": candidate_scenes,
            "platform_sops": [],
            "prompt_sops": [],
            "facts": {},
            "risk_flags": [],
            "missing_requirements": [],
        }

    return {
        "query": query,
        "route_query": effective_route_query,
        "route_trace": route_trace,
        "knowledge_trace": knowledge_trace,
        "shadow_decision": {
            "shadow_only": True,
            "allow_enter_prompt": False,
            "allow_replace_policy_scene": False,
            "allow_override_final_reply": False,
            "reason": "runtime_v2 shadow trace only",
        },
    }


if __name__ == "__main__":
    import json

    demo_cases = [
        {
            "query": "好的",
            "route_query": "用户：什么时候发货\n用户：好的",
        },
        {
            "query": "亲我单独拍的话还能优惠10块钱吗",
            "route_query": "用户：525839399303\n用户：亲我单独拍的话还能优惠10块钱吗",
        },
        {
            "query": "保质期多长时间",
            "route_query": "用户：保质期多长时间",
        },
    ]

    for c in demo_cases:
        print("=" * 80)
        print(c["query"])
        print(json.dumps(
            build_runtime_v2_shadow_trace(
                c["query"],
                route_query=c.get("route_query"),
            ),
            ensure_ascii=False,
            indent=2,
        ))
