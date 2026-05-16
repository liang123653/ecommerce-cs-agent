#!/usr/bin/env bash
set -e

HOST="${HOST:-http://127.0.0.1:8002}"
USER_ID="api_demo_user_001"
CONV_ID="api_demo_conv_001"

echo "================================================================================"
echo "HEALTH"
curl -s "$HOST/health" | python -m json.tool

echo "================================================================================"
echo "TURN 1"
curl -s -X POST "$HOST/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"这个耳机支持主动降噪吗？\",
    \"user_id\": \"$USER_ID\",
    \"conversation_id\": \"$CONV_ID\",
    \"debug\": true
  }" | tee /tmp/api_turn1.json | python -m json.tool

echo "================================================================================"
echo "HISTORY DEBUG"
curl -s -X POST "$HOST/debug/history" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"query\": \"你们之前说支持主动降噪，结果收到后根本没有，怎么办？\"
  }" | tee /tmp/api_history.json | python -m json.tool

echo "================================================================================"
echo "TURN 2"
curl -s -X POST "$HOST/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"你们之前说支持主动降噪，结果收到后根本没有，怎么办？\",
    \"user_id\": \"$USER_ID\",
    \"conversation_id\": \"$CONV_ID\",
    \"debug\": true
  }" | tee /tmp/api_turn2.json | python -m json.tool

echo "================================================================================"
echo "ASSERT"
python - <<'PY'
import json
from pathlib import Path

t1 = json.loads(Path("/tmp/api_turn1.json").read_text(encoding="utf-8"))
h = json.loads(Path("/tmp/api_history.json").read_text(encoding="utf-8"))
t2 = json.loads(Path("/tmp/api_turn2.json").read_text(encoding="utf-8"))

assert t1.get("memory_write", {}).get("written") is True, t1
assert h.get("has_history") is True, h
assert t2.get("memory_write", {}).get("written") is True, t2

print("turn1_memory_write:", t1.get("memory_write"))
print("history_has_history:", h.get("has_history"))
print("history_risk_level:", h.get("risk_level"))
print("turn2_strategy:", t2.get("strategy"))
print("turn2_context_fallback_used:", t2.get("context_fallback_used"))
print("PASS")
PY
