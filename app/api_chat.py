# -*- coding: utf-8 -*-
"""
FastAPI chat demo for ecommerce customer-service agent.

特点：
- 不改旧主链路；
- 调用 answer_with_strategy_and_memory_write；
- 支持 runtime memory write；
- 支持下一轮基于 user_id / conversation_id 读取历史；
- 返回 strategy / scene / memory_write / context_fallback_used，方便 demo 和调试。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="Ecommerce Customer Service Agent",
    description="RAG + SOP + business facts + memory guard + safety controlled customer-service agent.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户当前输入")
    user_id: str = Field("demo_user", description="用户 ID，用于多轮记忆")
    conversation_id: Optional[str] = Field(None, description="会话 ID，用于多轮记忆")
    product_id: Optional[str] = Field(None, description="商品 ID，可选")
    order_id: Optional[str] = Field(None, description="订单 ID，可选")
    debug: bool = Field(False, description="是否返回更多调试字段")


class ChatResponse(BaseModel):
    reply: str
    user_id: str
    conversation_id: str
    strategy: Optional[str] = None
    strategy_reason: Optional[str] = None
    scene: Optional[str] = None
    policy_file: Optional[str] = None
    context_fallback_used: Optional[bool] = None
    context_fallback_version: Optional[str] = None
    history_risk_level: Optional[str] = None
    memory_write: Dict[str, Any] = {}
    fallback_used: Optional[bool] = None
    safe: Optional[bool] = None
    debug: Optional[Dict[str, Any]] = None


class HistoryDebugRequest(BaseModel):
    user_id: str
    query: str
    product_id: Optional[str] = None
    order_id: Optional[str] = None


def _json_safe(obj: Any) -> Any:
    """把非 JSON 可序列化对象转成普通 dict/list/str。"""
    return json.loads(json.dumps(obj, ensure_ascii=False, default=str))


def _env_flag(name: str) -> str:
    return os.getenv(name, "0")


@app.get("/health")
def health() -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ok": True,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "env": {
            "USE_CONVERSATION_MEMORY": _env_flag("USE_CONVERSATION_MEMORY"),
            "USE_CONVERSATION_MEMORY_WRITE": _env_flag("USE_CONVERSATION_MEMORY_WRITE"),
            "USE_CONTEXT_AWARE_FALLBACK": _env_flag("USE_CONTEXT_AWARE_FALLBACK"),
            "USE_CONTEXT_AWARE_FALLBACK_FAST": _env_flag("USE_CONTEXT_AWARE_FALLBACK_FAST"),
        },
    }

    try:
        from memory.conversation_store import DB_PATH

        payload["memory_db_path"] = str(DB_PATH)
    except Exception as exc:
        payload["memory_db_error"] = str(exc)

    return payload


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    from app.memory_write_path import answer_with_strategy_and_memory_write

    conversation_id = req.conversation_id or f"conv_{req.user_id}"

    result = answer_with_strategy_and_memory_write(
        req.message,
        user_id=req.user_id,
        conversation_id=conversation_id,
        product_id=req.product_id,
        order_id=req.order_id,
    )

    debug_payload: Optional[Dict[str, Any]] = None

    if req.debug:
        debug_payload = {
            "mainline_used": result.get("mainline_used"),
            "retriever": result.get("retriever"),
            "retrieved_chunks": result.get("retrieved_chunks"),
            "validation_errors": result.get("validation_errors"),
            "llm_validation_errors": result.get("llm_validation_errors"),
            "sop_card_direct_used": result.get("sop_card_direct_used"),
            "metadata_gate": result.get("metadata_gate"),
            "history_summary": result.get("history_summary"),
            "business_summary": result.get("business_summary"),
        }
        debug_payload = _json_safe(debug_payload)

    bad_hits = result.get("bad_hits") or []
    validation_errors = result.get("validation_errors") or []

    safe = not bool(bad_hits or validation_errors)

    return ChatResponse(
        reply=result.get("reply") or "",
        user_id=req.user_id,
        conversation_id=conversation_id,
        strategy=result.get("strategy"),
        strategy_reason=result.get("strategy_reason"),
        scene=result.get("scene"),
        policy_file=result.get("policy_file"),
        context_fallback_used=result.get("context_fallback_used"),
        context_fallback_version=result.get("context_fallback_version"),
        history_risk_level=result.get("history_risk_level"),
        memory_write=_json_safe(result.get("memory_write") or {}),
        fallback_used=result.get("fallback_used"),
        safe=safe,
        debug=debug_payload,
    )


@app.post("/debug/history")
def debug_history(req: HistoryDebugRequest) -> Dict[str, Any]:
    """
    调试某个用户当前 query 能否召回历史。
    """
    from app.pipeline_llm import retrieve_history_auto

    history = retrieve_history_auto(
        user_query=req.query,
        user_id=req.user_id,
        product_id=req.product_id,
        order_id=req.order_id,
    )

    return _json_safe(history)
