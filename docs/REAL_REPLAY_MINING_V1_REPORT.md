# Real Replay Mining v1 Report

## 1. Input Files

- main_replay: `data/eval/phase15/phase15d_context_query_strategy_best_of_variants.jsonl`
- dpo_candidates: `data/processed/real_dialogues/dpo_pairs_candidate.jsonl`

## 2. Main Replay Overview

- total_rows: 5997
- no_hit_or_weak_count: 619 (10.32%)
- scene_mismatch_count: 4233 (70.59%)
- low_score_count: 2421 (40.37%)

### hit_status distribution

| hit_status | count | rate |
|---|---:|---:|
| scene_mismatch | 3713 | 61.91% |
| hit | 1043 | 17.39% |
| low_score | 622 | 10.37% |
| weak_query | 337 | 5.62% |
| no_hit | 282 | 4.70% |

### expected_scene distribution top 30

| scene | count | rate |
|---|---:|---:|
| unknown | 606 | 10.11% |
| promotion_policy | 579 | 9.65% |
| express_policy | 541 | 9.02% |
| shipping_policy | 401 | 6.69% |
| product_qa_policy | 355 | 5.92% |
| coupon_policy | 299 | 4.99% |
| gift_policy | 284 | 4.74% |
| shipping_fee_policy | 274 | 4.57% |
| quality_issue | 255 | 4.25% |
| stock_policy | 253 | 4.22% |
| order_modify_policy | 241 | 4.02% |
| logistics_policy | 240 | 4.00% |
| refund_policy | 221 | 3.69% |
| return_exchange | 216 | 3.60% |
| invoice_policy | 214 | 3.57% |
| price_protection | 207 | 3.45% |
| bulk_purchase_policy | 205 | 3.42% |
| missing_package_policy | 204 | 3.40% |
| description_mismatch | 202 | 3.37% |
| complaint_policy | 200 | 3.34% |

### top1_scene distribution top 30

| top1_scene | count | rate |
|---|---:|---:|
| logistics_policy | 1444 | 24.08% |
| return_exchange | 1023 | 17.06% |
| quality_issue | 704 | 11.74% |
| unknown | 603 | 10.06% |
| shipping_policy | 535 | 8.92% |
| refund_policy | 309 | 5.15% |
| order_modify_policy | 261 | 4.35% |
| express_policy | 245 | 4.09% |
| shipping_fee_policy | 193 | 3.22% |
| gift_policy | 193 | 3.22% |
| description_mismatch | 193 | 3.22% |
| service_recovery | 144 | 2.40% |
| promotion_policy | 92 | 1.53% |
| invoice_policy | 58 | 0.97% |

### chosen_strategy distribution

| strategy | count | rate |
|---|---:|---:|
| first_last_concat | 3831 | 63.88% |
| last_only | 1514 | 25.25% |
| first_only | 652 | 10.87% |

## 3. Output Pools

- no_hit_or_weak sample: `data/eval/real_replay_mining_v1/no_hit_or_weak_query_sample.jsonl`
- scene_mismatch sample: `data/eval/real_replay_mining_v1/scene_mismatch_sample.jsonl`
- low_score sample: `data/eval/real_replay_mining_v1/low_score_sample.jsonl`
- dpo audit sample: `data/eval/real_replay_mining_v1/dpo_candidate_audit_sample.jsonl`

## 4. DPO Candidate Overview

- dpo_candidate_rows: 50000

### DPO automatic issue counts

| issue | count |
|---|---:|
| rejected_too_short | 36921 |
| chosen_too_short | 36618 |
| same_chosen_rejected | 160 |
| chosen_possible_overpromise | 6 |

## 5. Interpretation

- This report is a lightweight real replay mining report.
- It does not call LLM generation.
- It should be used to decide which samples enter SOP review, SFT data construction, or DPO pair audit.
- DPO candidates are not treated as training-ready until reviewed.
