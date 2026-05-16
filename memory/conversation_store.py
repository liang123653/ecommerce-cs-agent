import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "database" / "ecommerce.db"


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


def query_messages(
    user_id: str,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    查询用户历史消息。

    如果同时有 order_id 和 product_id，使用 OR 召回：
    售前咨询通常没有 order_id，但会绑定 product_id。
    """
    conn = get_conn()
    cur = conn.cursor()

    if order_id and product_id:
        cur.execute("""
        SELECT *
        FROM conversation_messages
        WHERE user_id = ?
          AND (order_id = ? OR product_id = ?)
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, order_id, product_id, limit))
    elif order_id:
        cur.execute("""
        SELECT *
        FROM conversation_messages
        WHERE user_id = ?
          AND order_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, order_id, limit))
    elif product_id:
        cur.execute("""
        SELECT *
        FROM conversation_messages
        WHERE user_id = ?
          AND product_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, product_id, limit))
    else:
        cur.execute("""
        SELECT *
        FROM conversation_messages
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, limit))

    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))


def query_summaries(
    user_id: str,
    product_id: Optional[str] = None,
    order_id: Optional[str] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    查询历史会话摘要。
    """
    conn = get_conn()
    cur = conn.cursor()

    if order_id and product_id:
        cur.execute("""
        SELECT *
        FROM conversation_summaries
        WHERE user_id = ?
          AND (order_id = ? OR product_id = ?)
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, order_id, product_id, limit))
    elif order_id:
        cur.execute("""
        SELECT *
        FROM conversation_summaries
        WHERE user_id = ?
          AND order_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, order_id, limit))
    elif product_id:
        cur.execute("""
        SELECT *
        FROM conversation_summaries
        WHERE user_id = ?
          AND product_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, product_id, limit))
    else:
        cur.execute("""
        SELECT *
        FROM conversation_summaries
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (user_id, limit))

    rows = cur.fetchall()
    conn.close()
    return rows
