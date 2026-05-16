from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[1] / "knowledge_base"

SCENE_KEYWORDS = {
    "price_protection": ["降价", "价保", "补差价", "退差价", "买贵", "价格变低", "便宜"],
    "return_exchange": ["退", "换", "不合适", "尺码", "吊牌", "穿过", "洗过", "试穿", "颜色不喜欢"],
    "shipping_policy": ["发货", "待发货", "催发", "什么时候发", "出库", "急用"],
    "logistics_policy": ["物流", "快递", "签收", "没收到", "派送", "驿站", "丢件", "不动"],
    "refund_policy": ["退款", "到账", "钱", "退到哪里"],
    "quality_issue": ["质量", "坏", "破", "开胶", "裂", "瑕疵", "不能用", "污渍"],
    "complaint_policy": ["投诉", "骗人", "差评", "生气", "无语", "客服不处理", "服务差"],
}

FILE_MAP = {
    "price_protection": "price_protection.md",
    "return_exchange": "return_exchange.md",
    "shipping_policy": "shipping_policy.md",
    "logistics_policy": "logistics_policy.md",
    "refund_policy": "refund_policy.md",
    "quality_issue": "quality_issue.md",
    "complaint_policy": "complaint_policy.md",
}

def detect_scene(query: str) -> str:
    scores = {}
    for scene, keywords in SCENE_KEYWORDS.items():
        scores[scene] = sum(1 for kw in keywords if kw in query)
    best_scene = max(scores, key=scores.get)
    if scores[best_scene] == 0:
        return "return_exchange"
    return best_scene

def retrieve_policy(query: str):
    scene = detect_scene(query)
    file_name = FILE_MAP[scene]
    content = (KB_DIR / file_name).read_text(encoding="utf-8")
    return {
        "scene": scene,
        "file_name": file_name,
        "content": content
    }
