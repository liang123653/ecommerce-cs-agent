from typing import Optional, Dict, Any


# 本地模拟商品中心。
# 真实业务中这里应该对接商品中心 / ERP / PIM / 店铺商品详情接口。
MOCK_PRODUCTS = {
    "P_EARPHONE_001": {
        "product_id": "P_EARPHONE_001",
        "category": "数码耳机",
        "title": "无线蓝牙耳机",
        "attributes": {
            "降噪类型": "被动降噪",
            "防水等级": "IPX4",
            "蓝牙版本": "5.3",
            "续航": "约6小时",
        },
        "selling_points": ["高清通话", "低延迟", "轻量佩戴"],
        "special_notes": "页面实际标注为被动降噪，不应直接承诺主动降噪。",
    },
    "P_FOOD_001": {
        "product_id": "P_FOOD_001",
        "category": "食品",
        "title": "坚果燕麦棒",
        "attributes": {
            "保质期": "180天",
            "配料": "燕麦、坚果、蜂蜜",
            "储存方式": "阴凉干燥处保存",
        },
        "selling_points": ["代餐", "便携"],
        "special_notes": "食品类售后需结合拆封状态、保质期和页面配料说明判断。",
    },
    "P_VIRTUAL_001": {
        "product_id": "P_VIRTUAL_001",
        "category": "虚拟权益",
        "title": "学习会员月卡",
        "attributes": {
            "权益范围": "部分课程免费观看",
            "有效期": "30天",
            "到账方式": "购买后自动到账",
        },
        "selling_points": ["会员权益", "线上使用"],
        "special_notes": "虚拟商品需重点核实权益范围、到账状态和使用条件。",
    },
    "P_COAT_001": {
        "product_id": "P_COAT_001",
        "category": "服饰",
        "title": "春季女款外套",
        "attributes": {
            "面料": "聚酯纤维",
            "版型": "常规",
            "尺码建议": "需结合身高体重和肩宽胸围判断",
        },
        "selling_points": ["春季外套", "通勤"],
        "special_notes": "服饰尺码问题通常优先按退换货规则判断。",
    },
}


def query_product(product_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not product_id:
        return None
    return MOCK_PRODUCTS.get(product_id)


def format_product_info(product: Optional[Dict[str, Any]]) -> str:
    if not product:
        return "未查询到商品中心信息。"

    attrs = product.get("attributes") or {}
    attr_text = "；".join([f"{k}: {v}" for k, v in attrs.items()]) or "无"

    selling_points = "、".join(product.get("selling_points") or []) or "无"

    return (
        f"商品ID：{product.get('product_id')}\n"
        f"商品名称：{product.get('title')}\n"
        f"商品类目：{product.get('category')}\n"
        f"商品属性：{attr_text}\n"
        f"卖点信息：{selling_points}\n"
        f"特别说明：{product.get('special_notes') or '无'}"
    )
