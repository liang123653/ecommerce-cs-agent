# Real Replay Mining v1 Decision Summary

## 1. Source Pools

| source_pool | rows |
|---|---:|
| no_hit_or_weak | 300 |
| scene_mismatch | 300 |
| low_score | 300 |
| dpo_audit | 300 |

## 2. Suggested Action Buckets

| bucket | rows | suggested_next_action |
|---|---:|---|
| merchant_fact_gap | 431 | Do not train first. Build merchant/product/activity/fact layer or mock fact cards. |
| dpo_needs_rewrite_or_drop | 276 | Short pair. Rewrite or drop before training. |
| retrieval_or_policy_priority_gap | 187 | Inspect top cards and adjust retrieval priority / gate / policy precedence. |
| low_info_context_needed | 168 | Do not expand SOP. Improve context retrieval / memory / query construction. |
| platform_sop_or_retrieval_gap | 80 | Review whether platform SOP exists or retrieval failed to recall it. |
| taxonomy_or_label_gap | 34 | Review label taxonomy. Do not treat as retrieval failure directly. |
| dpo_needs_manual_review | 22 | Manual review needed. |
| dpo_keep_candidate | 1 | Can enter DPO review queue. |
| dpo_drop_same_pair | 1 | Drop from DPO. |

## 3. Key Decisions

1. Do not run SFT/DPO directly from the current real replay assets.
2. Most product/promotion/stock/gift/coupon cases should go to merchant fact modeling, not platform SOP expansion.
3. Weak-query cases should go to context/memory/query construction, not keyword rules.
4. Platform SOP/retrieval gap cases should be reviewed separately from merchant fact gaps.
5. DPO candidates require filtering and manual review before training.

## 4. Output Files

- `data/eval/real_replay_mining_v1/action_buckets/dpo_drop_same_pair.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/dpo_keep_candidate.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/dpo_needs_manual_review.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/dpo_needs_rewrite_or_drop.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/low_info_context_needed.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/merchant_fact_gap.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/platform_sop_or_retrieval_gap.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/retrieval_or_policy_priority_gap.jsonl`
- `data/eval/real_replay_mining_v1/action_buckets/taxonomy_or_label_gap.jsonl`
