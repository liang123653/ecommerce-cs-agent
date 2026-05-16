"""
Phase 7.9 高频业务意图路由器

目的：
1. 不再为每个具体问法单独写 SOP；
2. 先把真实客服高频问题归入稳定的“业务意图族”；
3. 对 coupon / invoice / express / gift / product_qa 等当前 RAG 容易误判的场景做强规则兜底；
4. 规则只负责“分流到业务族”，具体回复仍交给 SOP + 业务事实 + LLM 生成。
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


SceneResult = Dict[str, object]


SCENE_TO_FILE = {
    "promotion_policy": "promotion_policy.md",
    "coupon_policy": "coupon_policy.md",
    "invoice_policy": "invoice_policy.md",
    "express_policy": "express_policy.md",
    "shipping_fee_policy": "shipping_fee_policy.md",
    "gift_policy": "gift_policy.md",
    "product_qa_policy": "product_qa_policy.md",
    "stock_policy": "stock_policy.md",
    "order_modify_policy": "order_modify_policy.md",
    "missing_package_policy": "missing_package_policy.md",
    "bulk_purchase_policy": "bulk_purchase_policy.md",
    "shipping_policy": "shipping_policy.md",
    "logistics_policy": "logistics_policy.md",
    "refund_policy": "refund_policy.md",
    "return_exchange": "return_exchange.md",
    "quality_issue": "quality_issue.md",
    "description_mismatch": "description_mismatch_policy.md",
    "complaint_policy": "complaint_policy.md",
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _extract_last_user_text(text: str) -> str:
    """
    route_query 通常长这样：
        用户：xxx
        客服：yyy
        用户：zzz

    优先使用最后一个用户 turn，因为当前轮意图最重要。
    """
    text = text or ""
    last = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("用户："):
            last = line.split("用户：", 1)[1].strip()
    return _norm(last or text)


def _has_any(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if kw in text]


def _result(scene: str, score: int, hits: List[str], reason: str) -> SceneResult:
    return {
        "scene": scene,
        "file_name": SCENE_TO_FILE[scene],
        "score": score,
        "hits": hits,
        "router_source": "phase7_9_high_freq_rules",
        "router_reason": reason,
    }


def detect_high_frequency_scene(route_query: str) -> Optional[SceneResult]:
    """
    返回强规则命中的高频场景；未命中返回 None，交给原有 RAG/LLM 路由。

    设计原则：
    - 只覆盖边界清晰的高频业务族；
    - 不追求枚举所有问题；
    - 当前用户 turn 权重高于历史上下文；
    - 对“发什么快递”和“物流异常”做明确拆分；
    - 对“优惠券”和“普通优惠”做明确拆分。
    """
    full = _norm(route_query)
    last = _extract_last_user_text(route_query)

    # 1. 高风险情绪/投诉优先。注意：轻微“无语/太慢”可能也可按底层问题处理，
    # 但如果出现明确投诉/骗人/差评等，应优先进入投诉安抚流程。
    hits = _has_any(last + full, ["投诉", "差评", "骗人", "不讲道理", "态度", "骂", "炸了", "不靠谱", "假的"])
    if hits:
        return _result("complaint_policy", 100 + len(hits), hits, "命中明确投诉或强烈不满表达")

    # 2. 描述不符/售前承诺不一致。
    # 排除普通发货承诺，否则“不是说今天发货吗”会误判。
    desc_hits = _has_any(last + full, ["描述不符", "页面写", "详情页", "图片上", "你们说", "客服说", "不是说", "和说的不一样", "页面上都写"])
    shipping_promise_hits = _has_any(last, ["今天发", "明天发", "发货", "没发", "什么时候发"])
    if desc_hits and not shipping_promise_hits:
        return _result("description_mismatch", 95 + len(desc_hits), desc_hits, "命中页面描述/历史承诺不一致表达")

    # 3. 发票/收据。
    hits = _has_any(last + full, ["发票", "开票", "收据", "抬头", "税号", "纳税人", "增值税", "专票", "普票", "报销"])
    if hits:
        return _result("invoice_policy", 90 + len(hits), hits, "命中发票/开票/抬头/税号咨询")

    # 4. 优惠券：必须和普通优惠分开。
    hits = _has_any(last + full, ["优惠券", "购物券", "券", "领券", "领取", "领不了", "不能领取", "用不了", "满减券"])
    if hits:
        return _result("coupon_policy", 88 + len(hits), hits, "命中优惠券领取/使用问题")

    # 5. 快递方式咨询：和物流异常拆开。
    express_hits = _has_any(last + full, [
        "发什么快递", "什么快递", "哪家快递", "寄哪家", "默认快递", "可以发", "能发",
        "申通", "中通", "圆通", "韵达", "百世", "汇通", "天天", "邮政", "EMS", "顺丰", "快递方式"
    ])
    logistics_problem_hits = _has_any(last, ["物流", "签收", "没收到", "没有收到", "驿站", "派件", "揽收", "单号", "退回", "丢", "催快递"])
    if express_hits and not logistics_problem_hits:
        return _result("express_policy", 86 + len(express_hits), express_hits, "命中发货快递方式/指定快递咨询")

    # 6. 运费/包邮。
    hits = _has_any(last + full, ["包邮", "运费", "邮费", "快递费", "免运费", "补邮", "到付"])
    if hits:
        return _result("shipping_fee_policy", 84 + len(hits), hits, "命中包邮/运费/邮费问题")

    # 7. 赠品/试吃/送什么。
    hits = _has_any(last + full, ["赠品", "送什么", "送不送", "有没有送", "试吃", "核桃夹", "夹子", "湿巾", "开口器", "礼品袋", "礼袋"])
    if hits:
        return _result("gift_policy", 82 + len(hits), hits, "命中赠品/试吃/随单赠送问题")

    # 8. 少件/漏发/少送。
    hits = _has_any(last + full, ["少件", "漏发", "少发", "少了", "没送", "没有送", "少送", "没放", "没有放", "缺件"])
    if hits:
        return _result("missing_package_policy", 80 + len(hits), hits, "命中少件/漏发/少送问题")

    # 9. 改地址/备注/拍错/定制信息修改。
    hits = _has_any(last + full, ["改地址", "地址不对", "地址错", "改电话", "电话少", "备注", "拍错", "发错", "不要发错", "换成", "帮我改"])
    if hits:
        return _result("order_modify_policy", 78 + len(hits), hits, "命中订单信息修改/备注/拍错调整")

    # 10. 库存/上下架/预售/缺货。
    hits = _has_any(last + full, ["有货", "没货", "缺货", "什么时候有货", "什么时候到货", "预售", "下架", "到新货", "库存"])
    if hits:
        return _result("stock_policy", 76 + len(hits), hits, "命中库存/预售/到货时间咨询")

    # 11. 批发/大量购买/团购/定制大单。
    hits = _has_any(last + full, ["批发", "大量", "团购", "买多", "买几十", "100支", "200支", "100个", "200个", "几百", "定制", "起订"])
    if hits:
        return _result("bulk_purchase_policy", 74 + len(hits), hits, "命中批发/大量购买/定制大单咨询")

    # 12. 商品参数/口味/颜色/材质/尺寸等售前问答。
    hits = _has_any(last + full, [
        "尺寸", "多大", "材质", "纯棉", "无纺布", "颜色", "红色", "黑色", "口味", "味道", "好吃",
        "甜", "咸", "奶油", "椒盐", "原味", "软", "硬", "厚", "薄", "吸水", "生产日期", "保质期",
        "配料", "成分", "荧光", "干湿两用", "盖子", "规格", "型号", "一包多少", "多少克"
    ])
    if hits:
        return _result("product_qa_policy", 72 + len(hits), hits, "命中商品参数/口味/材质/尺寸咨询")

    # 13. 普通优惠/活动/改价。
    hits = _has_any(last + full, ["优惠", "便宜", "少点", "活动", "满减", "买一送一", "买二送一", "聚划算", "改价", "最低价", "特价", "划算"])
    if hits:
        return _result("promotion_policy", 70 + len(hits), hits, "命中普通优惠/活动/改价咨询")

    return None


def route_with_high_freq_rules(route_query: str, base_retriever) -> SceneResult:
    """
    用法：
        policy = route_with_high_freq_rules(query, retrieve_policy_auto)

    如果强规则命中，直接返回高频业务族；
    否则走原有 retrieve_policy_auto。
    """
    hit = detect_high_frequency_scene(route_query)
    if hit:
        return hit

    base = base_retriever(route_query)
    if isinstance(base, dict):
        base.setdefault("router_source", "base_retrieve_policy_auto")
    return base
