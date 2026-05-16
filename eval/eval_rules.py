from app.pipeline import answer

EVAL_SET = [
    {
        "query": "刚买就降价了怎么办",
        "must_include": ["价保"],
        "must_not_include": ["退货重拍", "一定退"],
    },
    {
        "query": "我穿了一次还能退吗",
        "must_include": ["二次销售"],
        "must_not_include": ["一定可以退"],
    },
    {
        "query": "这个有质量问题怎么处理",
        "must_include": ["照片", "售后"],
        "must_not_include": ["一定赔偿"],
    },
    {
        "query": "怎么还没发货",
        "must_include": ["订单号"],
        "must_not_include": ["系统故障"],
    },
]

def run_eval():
    total = len(EVAL_SET)
    passed = 0

    for item in EVAL_SET:
        result = answer(item["query"])
        reply = result["reply"]

        ok_include = all(word in reply for word in item["must_include"])
        ok_exclude = all(word not in reply for word in item["must_not_include"])
        ok = ok_include and ok_exclude
        passed += int(ok)

        print("=" * 80)
        print("问题:", item["query"])
        print("回复:", reply)
        print("通过:", ok)

    print("=" * 80)
    print(f"规则评测通过率: {passed}/{total} = {passed / total:.2%}")

if __name__ == "__main__":
    run_eval()
