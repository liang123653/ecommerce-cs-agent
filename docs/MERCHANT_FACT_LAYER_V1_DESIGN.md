# Merchant Fact Layer v1 Design

## 1. Background

Real Replay Mining v1 shows that the largest failure bucket is:

```text
merchant_fact_gap: 431

This means many real customer-service queries are not mainly platform policy problems. They require merchant-side or product-side facts, such as:

product attributes
product availability
promotion rules
coupon rules
gift rules
stock status
bulk purchase support
invoice support
shipping fee configuration
express / delivery configuration
order modification support

These should not be solved by adding keyword rules or expanding platform SOP blindly.

2. Design Goal

Build a lightweight merchant/product/activity fact layer that can be queried before or alongside SOP/RAG.

The goal is not to replace SOP retrieval, but to separate:

platform policy knowledge
vs
merchant/product/activity facts
3. Supported Fact Groups
product_fact

Examples:

material
size/specification
ingredients
color
function
compatibility
shelf life
production date
origin
product difference
promotion_fact

Examples:

full reduction
buy-one-get-one
discount
price activity
activity time
whether multiple offers can be combined
coupon_fact

Examples:

coupon threshold
coupon availability
coupon expiration
whether coupon can be reissued
gift_fact

Examples:

whether gift exists
gift quantity
gift condition
whether gift can be replaced
whether missing gift can be handled
stock_fact

Examples:

whether in stock
whether restock is available
whether preorder is supported
SKU-level stock difference
invoice_fact

Examples:

whether invoice is supported
invoice type
invoice title requirement
invoice issuing time
shipping_config_fact

Examples:

shipping fee
free shipping threshold
supported courier
whether specific courier can be selected
whether self-pickup is supported
order_modify_fact

Examples:

address modification
SKU modification
cancellation before shipment
merge shipment
remark modification
4. Fact Contract

Each fact card should follow this structure:

{
  "fact_id": "product_fact_0001",
  "fact_group": "product_fact",
  "product_id": "optional",
  "sku_id": "optional",
  "scope": "product|shop|activity|order",
  "title": "fact title",
  "facts": {
    "key": "value"
  },
  "customer_reply_guidance": "客服可说的话",
  "do_not_say": [
    "不能无依据承诺"
  ],
  "need_human_conditions": [
    "页面信息与实物不一致",
    "用户提供截图与系统事实冲突"
  ],
  "updated_at": "YYYY-MM-DD"
}
5. Runtime Usage

The runtime flow should be:

user query
  -> answer_strategy
  -> if merchant/product/activity fact needed:
       query merchant fact layer
  -> query SOP/RAG when platform policy is needed
  -> combine fact + SOP + order state
  -> generate controlled reply
6. Boundary

The fact layer should answer:

what the product/shop/activity says
what can be verified from structured facts
what needs user screenshot or order information

The fact layer should not decide:

final refund approval
final compensation responsibility
final platform dispute judgment
guaranteed delivery or replacement
7. Why This Comes Before SFT/DPO

Real Replay Mining v1 shows that many failures are caused by missing merchant/product/activity facts.

If we train SFT/DPO before fixing fact availability, the model may learn to guess product or promotion information.

Therefore:

fact layer first
SFT/DPO later
8. Evaluation Plan

Create a merchant fact smoke set covering:

product QA
promotion
coupon
gift
stock
invoice
shipping configuration
order modification

Evaluate:

whether fact layer is triggered
whether reply avoids guessing
whether reply asks for missing product/order evidence
whether no unsafe promise is made
