# Merchant Fact Layer v1 Smoke Report

## 1. Background

Real Replay Mining v1 showed that the largest action bucket is:

```text
merchant_fact_gap: 431

This means many real customer-service queries require merchant-side, product-side, or activity-side facts instead of platform SOP knowledge.

Main missing areas include:

product QA
promotion
coupon
gift
stock
invoice
shipping configuration
order modification
bulk purchase
2. Implementation

Added:

data/merchant_facts/mock_merchant_facts.jsonl
tools/merchant_fact_tool.py
eval/smoke_merchant_fact_tool_v1.py

The merchant fact layer is currently isolated and not directly connected to the mainline.

3. Smoke Result

Smoke cases: 9

fact group	result
product_fact	passed
promotion_fact	passed
coupon_fact	passed
gift_fact	passed
stock_fact	passed
invoice_fact	passed
shipping_config_fact	passed
order_modify_fact	passed
bulk_purchase_fact	passed

Overall:

total: 9
passed: 9
pass_rate: 1.0
4. Boundary

The fact layer does not replace platform SOP.

It only provides merchant/product/activity facts and safe customer reply guidance.

It must not decide:

final refund approval
final compensation responsibility
guaranteed shipment
guaranteed gift replacement
guaranteed coupon reissue
guaranteed stock availability
guaranteed invoice type
5. Key Engineering Decision

Real replay mining showed that the largest failure source is not model expression quality, but missing merchant/product/activity facts.

Therefore, the correct order is:

merchant fact layer first
SFT/DPO later

This avoids teaching the model to guess product, promotion, gift, stock, invoice, or shipping configuration facts.

6. Next Step

Integrate merchant fact retrieval as a guarded side context, not as a replacement for the existing SOP/RAG mainline.

The next integration should remain behind feature flags:

USE_MERCHANT_FACT_LAYER=1
USE_MERCHANT_FACT_SIDE_CONTEXT=1

The first mainline integration should only affect product, promotion, coupon, gift, stock, invoice, shipping configuration, order modification, and bulk purchase style queries.
