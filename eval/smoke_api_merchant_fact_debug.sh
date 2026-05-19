#!/usr/bin/env bash
set -e

HOST="${HOST:-http://127.0.0.1:8002}"

echo "================================================================================"
echo "MERCHANT FACT DEBUG: promotion"
curl --max-time 30 -s -X POST "$HOST/debug/merchant_fact" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "买二送一那买四送二吗？送几份？"
  }' | tee /tmp/merchant_fact_debug_promotion.json | python -m json.tool

echo "================================================================================"
echo "MERCHANT FACT DEBUG: product"
curl --max-time 30 -s -X POST "$HOST/debug/merchant_fact" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这个是纯棉的吗，会不会有荧光增白剂？"
  }' | tee /tmp/merchant_fact_debug_product.json | python -m json.tool

echo "================================================================================"
echo "ASSERT"
python - <<'PY'
import json
from pathlib import Path

promo = json.loads(Path("/tmp/merchant_fact_debug_promotion.json").read_text(encoding="utf-8"))
prod = json.loads(Path("/tmp/merchant_fact_debug_product.json").read_text(encoding="utf-8"))

assert promo.get("enabled") is True, promo
assert promo.get("hit") is True, promo
assert promo.get("top_fact_group") == "promotion_fact", promo
assert promo.get("note") == "shadow_only_not_used_as_final_reply", promo

assert prod.get("enabled") is True, prod
assert prod.get("hit") is True, prod
assert prod.get("top_fact_group") == "product_fact", prod
assert prod.get("note") == "shadow_only_not_used_as_final_reply", prod

print("promotion:", {
    "top_fact_id": promo.get("top_fact_id"),
    "top_fact_group": promo.get("top_fact_group"),
    "top_fact_score": promo.get("top_fact_score"),
})
print("product:", {
    "top_fact_id": prod.get("top_fact_id"),
    "top_fact_group": prod.get("top_fact_group"),
    "top_fact_score": prod.get("top_fact_score"),
})
print("PASS")
PY
