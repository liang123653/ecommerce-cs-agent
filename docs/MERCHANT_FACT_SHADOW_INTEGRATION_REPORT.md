# Merchant Fact Shadow Integration Report

## 1. Background

Real Replay Mining v1 showed that the largest action bucket is `merchant_fact_gap`.

Merchant Fact Layer v1 smoke passed:

- total: 9
- passed: 9
- pass_rate: 100%

## 2. Integration Scope

Added merchant fact shadow side context and debug endpoint.

Files:

- `tools/merchant_fact_tool.py`
- `app/merchant_fact_shadow.py`
- `app/memory_write_path.py`
- `app/api_chat.py`
- `eval/smoke_api_merchant_fact_debug.sh`

## 3. Runtime Flags

Merchant fact shadow is controlled by:

```bash
USE_MERCHANT_FACT_LAYER=1
USE_MERCHANT_FACT_SHADOW=1
4. Debug Endpoint

Added:

POST /debug/merchant_fact

This endpoint directly queries merchant fact shadow and does not call the main LLM path.

5. Smoke Result
Promotion query

Query:

买二送一那买四送二吗？送几份？

Observed:

enabled: true
hit: true
top_fact_id: promotion_fact_0001
top_fact_group: promotion_fact
top_fact_score: 0.7
note: shadow_only_not_used_as_final_reply
Product query

Query:

这个是纯棉的吗，会不会有荧光增白剂？

Observed:

enabled: true
hit: true
top_fact_id: product_fact_0001
top_fact_group: product_fact
top_fact_score: 0.7059
note: shadow_only_not_used_as_final_reply
6. Boundary

This integration does not:

change final customer reply
replace SOP/RAG
decide refund or compensation
guarantee gift, coupon, stock, shipping, invoice, or product attributes
train or enable SFT/DPO adapter

It only exposes merchant/product/activity fact hits as shadow side context.

7. Engineering Decision

The current system should keep merchant fact layer in shadow/debug mode first.

Next phase can be guarded integration:

merchant fact shadow
  -> observe hit quality
  -> guarded side context
  -> final reply still validated by safety rules

This follows the replay mining conclusion:

fact layer first
SFT/DPO later

