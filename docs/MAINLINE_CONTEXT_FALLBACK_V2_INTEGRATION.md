
## 8. Seeded Multiturn Gold Regression Analysis

The seeded multiturn gold regression with mainline context-aware fallback v2 produced:

- sample_size: 30
- safe_reply_rate: 100%
- behavior_pass_rate: 96.67%
- fast_context_fallback_rate: 23.33%
- mainline_used_rate: 20%

Compared with the previous seeded end-to-end baseline:

- behavior_pass_rate improved from 83.33% to 96.67%
- safe_reply_rate remained 100%

Remaining failed case:

- `mt_gold_003`
- expected_behavior: `return_exchange_safe`
- issue type: safe but too generic
- diagnosis: low-risk context fallback wording lacks after-sales/action specificity
- not a safety failure
- not a memory failure
- not a mainline runtime failure

Decision:

Do not patch this by adding sample-specific keywords such as size, exchange, or wearing. Keep it as a known low-risk template specificity issue and prioritize clean regression next.

## 9. Clean Business Pipeline Regression After Pending Evidence Repair

After adding the quality-issue pending-evidence final reply repair, the clean business pipeline regression passed.

Environment flags:

- `USE_CONVERSATION_MEMORY=1`
- `USE_CONTEXT_AWARE_FALLBACK=1`
- `USE_CONTEXT_AWARE_FALLBACK_FAST=1`

Result:

- total: 15
- scene_acc: 100%
- file_acc: 100%
- rule_hit_rate: 100%
- safety_rate: 100%
- overall_rate: 100%
- fallback_rate: 6.67%

The previous failing case:

- query: `订单 202604240004 商品有质量问题怎么处理？`
- scene: `quality_issue`
- file: `quality_issue.md`
- previous issue: final fallback reply dropped the order after-sales status `待用户补充凭证`
- repair: preserve pending-evidence order status in the final customer-visible reply

Conclusion:

The mainline context-aware fallback v2 integration does not break the existing business pipeline. The system now passes both multiturn memory guard regression and clean business pipeline regression.

## 10. Memory Write Path Smoke

A two-turn runtime memory write/read smoke test passed.

Test flow:

1. Turn 1 called `answer_with_strategy_and_memory_write`.
2. The user and assistant messages were persisted into `conversation_messages`.
3. A direct `retrieve_history_auto` call after Turn 1 returned `has_history=True`.
4. Turn 2 read the persisted history and triggered context-aware fallback v2 through the pre-strategy fast path.
5. Turn 2 was also written back to memory.

Observed result:

- turn1 memory_write: `written=True`
- direct memory check: `has_history=True`
- direct memory risk_level: `high`
- turn2 strategy: `CONTEXT_AWARE_FALLBACK`
- turn2 strategy_reason: `pre_strategy_high_risk_history_context`
- turn2 context_fallback_used: `True`
- turn2 context_fallback_version: `v2`
- turn2 memory_write: `written=True`

Conclusion:

The system now supports runtime memory write and next-turn memory read for guarded multiturn customer-service handling. This validates the first stage of memory write path integration without directly modifying the existing answer strategy core.

## 11. Clean Regression with Memory Write Enabled

After enabling runtime memory write, the clean business pipeline regression still passed.

Environment flags:

- `USE_CONVERSATION_MEMORY=1`
- `USE_CONVERSATION_MEMORY_WRITE=1`
- `USE_CONTEXT_AWARE_FALLBACK=1`
- `USE_CONTEXT_AWARE_FALLBACK_FAST=1`

Result:

- total: 15
- scene_acc: 100%
- file_acc: 100%
- rule_hit_rate: 100%
- safety_rate: 100%
- overall_rate: 100%
- fallback_rate: 6.67%

Conclusion:

Runtime memory writing does not break the existing business pipeline. The system now supports memory read, guarded context-aware fallback, and runtime message persistence under feature flags.

## 13. FastAPI Multiturn Smoke Result

The FastAPI `/chat` demo passed a two-turn multiturn memory smoke test.

Environment flags:

- `USE_CONVERSATION_MEMORY=1`
- `USE_CONVERSATION_MEMORY_WRITE=1`
- `USE_CONTEXT_AWARE_FALLBACK=1`
- `USE_CONTEXT_AWARE_FALLBACK_FAST=1`

Turn 1:

- endpoint: `POST /chat`
- strategy: `PRODUCT_KNOWLEDGE`
- memory_write.written: `true`

History debug:

- endpoint: `POST /debug/history`
- has_history: `true`
- risk_level: `high`
- retrieved previous user and assistant messages from the same user/conversation

Turn 2:

- endpoint: `POST /chat`
- strategy: `CONTEXT_AWARE_FALLBACK`
- strategy_reason: `pre_strategy_high_risk_history_context`
- context_fallback_used: `true`
- context_fallback_version: `v2`
- history_risk_level: `high`
- memory_write.written: `true`
- safe: `true`

Conclusion:

The project now exposes a local API demo for the controlled multiturn ecommerce customer-service agent. The demo validates runtime memory write, next-turn memory retrieval, and guarded context-aware fallback through the API layer.
