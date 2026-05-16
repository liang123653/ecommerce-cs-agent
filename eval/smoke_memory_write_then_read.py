# -*- coding: utf-8 -*-

from app.memory_write_path import answer_with_strategy_and_memory_write
from app.pipeline_llm import retrieve_history_auto

USER_ID = "smoke_memory_write_user"
CONV_ID = "smoke_memory_write_conv"

print("=" * 100)
print("TURN 1: write memory")

r1 = answer_with_strategy_and_memory_write(
    "这个耳机支持主动降噪吗？",
    user_id=USER_ID,
    conversation_id=CONV_ID,
)

print("strategy:", r1.get("strategy"))
print("reply:", r1.get("reply"))
print("memory_write:", r1.get("memory_write"))

print("=" * 100)
print("DIRECT MEMORY CHECK AFTER TURN 1")

h = retrieve_history_auto(
    user_query="你们之前说支持主动降噪，结果收到后根本没有，怎么办？",
    user_id=USER_ID,
    product_id=None,
    order_id=None,
)

print("has_history:", h.get("has_history"))
print("risk_level:", h.get("risk_level"))
print("risk_reason:", h.get("risk_reason"))
print("messages:", h.get("messages") or h.get("recent_messages"))

print("=" * 100)
print("TURN 2: read memory + answer")

r2 = answer_with_strategy_and_memory_write(
    "你们之前说支持主动降噪，结果收到后根本没有，怎么办？",
    user_id=USER_ID,
    conversation_id=CONV_ID,
)

print("strategy:", r2.get("strategy"))
print("strategy_reason:", r2.get("strategy_reason"))
print("context_fallback_used:", r2.get("context_fallback_used"))
print("context_fallback_version:", r2.get("context_fallback_version"))
print("history_risk_level:", r2.get("history_risk_level"))
print("reply:", r2.get("reply"))
print("memory_write:", r2.get("memory_write"))
