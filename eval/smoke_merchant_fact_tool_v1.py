# -*- coding: utf-8 -*-
from tools.merchant_fact_tool import query_merchant_facts, build_merchant_fact_reply

CASES = [
    {"query": "这个是纯棉的吗，会不会有荧光增白剂？", "expected_group": "product_fact"},
    {"query": "买二送一那买四送二吗？送几份？", "expected_group": "promotion_fact"},
    {"query": "优惠券还能补发吗？", "expected_group": "coupon_fact"},
    {"query": "赠品能换别的吗？", "expected_group": "gift_fact"},
    {"query": "还有货吗？什么时候补货？", "expected_group": "stock_fact"},
    {"query": "能开发票或者收据吗？", "expected_group": "invoice_fact"},
    {"query": "可以指定发邮政吗？运费怎么算？", "expected_group": "shipping_config_fact"},
    {"query": "我地址写错了还能改吗？", "expected_group": "order_modify_fact"},
    {"query": "买很多有批发价吗？", "expected_group": "bulk_purchase_fact"},
]

passed = 0

for i, c in enumerate(CASES, 1):
    r = query_merchant_facts(c["query"], top_k=3)
    top_group = r["facts"][0]["fact_group"] if r["facts"] else None
    ok = top_group == c["expected_group"]
    passed += int(ok)

    print("=" * 100)
    print(f"[{i}/{len(CASES)}]", c["query"])
    print("expected_group:", c["expected_group"])
    print("top_group:", top_group)
    print("hit:", r["hit"])
    print("ok:", ok)
    print("top_facts:", [(x.get("fact_id"), x.get("fact_group"), x.get("score")) for x in r["facts"]])
    print("reply:", build_merchant_fact_reply(c["query"], r))

print("=" * 100)
print({
    "total": len(CASES),
    "passed": passed,
    "pass_rate": round(passed / len(CASES), 4),
})
