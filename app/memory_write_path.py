# -*- coding: utf-8 -*-
"""
Runtime memory write wrapper.

目标：
- 不直接改 answer_strategy 主逻辑；
- 用 feature flag 控制是否写入；
- 每轮结束后写入 user/assistant 两条消息；
- 先支持 smoke 验证，再决定是否接入正式 API。
"""

from __future__ import annotations

import os
import inspect
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _get_db_path() -> Path:
    from memory.conversation_store import DB_PATH
    return Path(DB_PATH)


def _columns(conn: sqlite3.Connection, table: str) -> Dict[str, Dict[str, Any]]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {
        r[1]: {
            "cid": r[0],
            "name": r[1],
            "type": r[2],
            "notnull": r[3],
            "default": r[4],
            "pk": r[5],
        }
        for r in rows
    }


def _insert_dynamic(conn: sqlite3.Connection, table: str, values: Dict[str, Any]) -> None:
    cols = _columns(conn, table)
    insert_values = {}

    for k, v in values.items():
        if k in cols:
            insert_values[k] = v

    # 常见主键字段兜底：
    # 如果是 INTEGER PRIMARY KEY，必须交给 SQLite 自增，不能写 UUID，否则会 datatype mismatch。
    for id_col in ["id", "message_id", "summary_id"]:
        if id_col in cols and id_col not in insert_values:
            col = cols[id_col]
            col_type = str(col.get("type") or "").upper()
            is_pk = bool(col.get("pk"))
            if is_pk and "INT" in col_type:
                continue
            insert_values[id_col] = str(uuid4())

    # 常见时间字段兜底
    for time_col in ["created_at", "updated_at", "timestamp", "created_time"]:
        if time_col in cols and time_col not in insert_values:
            insert_values[time_col] = _now()

    if not insert_values:
        raise RuntimeError(f"No matched columns for table={table}. table_cols={list(cols)}")

    keys = list(insert_values.keys())
    placeholders = ", ".join(["?"] * len(keys))
    sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})"
    conn.execute(sql, [insert_values[k] for k in keys])


def write_turn_to_memory(
    *,
    user_id: str,
    conversation_id: str,
    user_query: str,
    assistant_reply: str,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    写入一轮 user/assistant 对话。

    只写 conversation_messages，不自动生成 summary。
    summary 后续单独做，避免本阶段引入过多复杂逻辑。
    """
    if not user_id:
        return {"written": False, "reason": "missing_user_id"}

    if not conversation_id:
        conversation_id = f"conv_{user_id}"

    db = _get_db_path()
    conn = sqlite3.connect(str(db))

    try:
        base = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "product_id": product_id,
            "order_id": order_id,
            "created_at": _now(),
            "updated_at": _now(),
            "timestamp": _now(),
        }

        _insert_dynamic(
            conn,
            "conversation_messages",
            {
                **base,
                "role": "user",
                "content": user_query,
                "message": user_query,
                "text": user_query,
            },
        )

        _insert_dynamic(
            conn,
            "conversation_messages",
            {
                **base,
                "role": "assistant",
                "content": assistant_reply,
                "message": assistant_reply,
                "text": assistant_reply,
            },
        )

        conn.commit()
        return {
            "written": True,
            "db_path": str(db),
            "conversation_id": conversation_id,
        }

    except Exception as e:
        conn.rollback()
        try:
            msg_cols = _columns(conn, "conversation_messages")
        except Exception:
            msg_cols = {}
        return {
            "written": False,
            "error": str(e),
            "db_path": str(db),
            "message_columns": {
                k: {
                    "type": v.get("type"),
                    "pk": v.get("pk"),
                    "notnull": v.get("notnull"),
                    "default": v.get("default"),
                }
                for k, v in msg_cols.items()
            },
        }

    finally:
        conn.close()


def answer_with_strategy_and_memory_write(
    query: str,
    *,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    旁路包装器：
    - 先调用原 answer_with_strategy；
    - 再按 feature flag 写入 memory；
    - 不影响原函数行为。
    """
    from app.answer_strategy import answer_with_strategy

    # 兼容不同版本的 answer_with_strategy 签名：
    # 有些版本支持 user_id/product_id，有些不支持 order_id。
    sig = inspect.signature(answer_with_strategy)
    kwargs = {}

    candidate_kwargs = {
        "user_id": user_id,
        "product_id": product_id,
        "order_id": order_id,
    }

    for k, v in candidate_kwargs.items():
        if k in sig.parameters:
            kwargs[k] = v

    result = answer_with_strategy(query, **kwargs)

    if os.getenv("USE_CONVERSATION_MEMORY_WRITE", "0") != "1":
        result["memory_write"] = {"written": False, "reason": "feature_flag_off"}
        return result

    reply = result.get("reply") or ""

    write_result = write_turn_to_memory(
        user_id=user_id or "",
        conversation_id=conversation_id or f"conv_{user_id}",
        user_query=query,
        assistant_reply=reply,
        product_id=product_id,
        order_id=order_id,
    )

    result["memory_write"] = write_result
    return result
