"""
Phase 7.9.3 文本归一化 + 当前轮路由边界修正

在 Phase 7.9.1 基础上修正几类明显真实问题：
1. 处理真实客服语料里的错别字/异体字/繁体字：优惠劵、沒有、為什麼、買、發、貨等；
2. 修复“优惠劵/开抢”没有进入 coupon_policy 的问题；
3. 修复“没有送/不送/多送/礼品袋/湿巾”等赠品问题的召回；
4. 修复“发百世汇通并备注加急”被 order_modify 抢走的问题；
5. 修复“包装严实点/包装好一点”这类发货前包装要求；
6. 尽量不追逐自动标签噪声，只处理明显业务路由漏召。
"""

from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional


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
    "price_protection": "price_protection.md",
    "unknown": "unknown_policy.md",
}


CHAR_MAP = str.maketrans({
    "劵": "券",
    "優": "优",
    "惠": "惠",
    "嗎": "吗",
    "麼": "么",
    "麽": "么",
    "為": "为",
    "買": "买",
    "賣": "卖",
    "沒": "没",
    "這": "这",
    "個": "个",
    "發": "发",
    "貨": "货",
    "運": "运",
    "費": "费",
    "單": "单",
    "質": "质",
    "題": "题",
    "後": "后",
    "裡": "里",
    "裏": "里",
    "會": "会",
    "讓": "让",
    "應": "应",
    "該": "该",
    "實": "实",
    "價": "价",
    "電": "电",
    "話": "话",
    "領": "领",
    "禮": "礼",
    "紙": "纸",
})


LOW_INFO_WORDS = {
    "好", "好的", "好吧", "嗯", "嗯嗯", "恩", "恩恩", "是", "是的", "对", "对的",
    "哦", "噢", "谢谢", "不客气", "在吗", "您好", "你好", "亲", "可以", "行",
    "那好吧", "拍了", "已拍", "知道了", "明白了", "不用了", "那我等回复吧",
}


def _norm(text: str) -> str:
    text = (text or "").translate(CHAR_MAP)
    text = text.replace("优惠劵", "优惠券")
    text = text.replace("為什么", "为什么")
    text = text.replace("為什麼", "为什么")
    return re.sub(r"\s+", "", text)


def _extract_user_turns(route_query: str) -> List[str]:
    turns: List[str] = []
    for line in (route_query or "").splitlines():
        line = line.strip()
        if line.startswith("用户："):
            turns.append(_norm(line.split("用户：", 1)[1]))
    if not turns and route_query:
        turns.append(_norm(route_query))
    return [x for x in turns if x]


def _extract_recent_text(route_query: str, recent_lines: int = 4) -> str:
    lines = [x.strip() for x in (route_query or "").splitlines() if x.strip()]
    return _norm("\n".join(lines[-recent_lines:]))


def _is_low_info(text: str) -> bool:
    text = _norm(text)
    if not text:
        return True
    if text in LOW_INFO_WORDS:
        return True
    if len(text) <= 2:
        return True
    if re.fullmatch(r"[0-9]+", text):
        return True
    return False


def _hits(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if kw in text]


def _mk(scene: str, score: int, hits: List[str], reason: str, scope: str) -> SceneResult:
    return {
        "scene": scene,
        "file_name": SCENE_TO_FILE[scene],
        "score": score,
        "hits": hits,
        "router_source": "phase7_9_3_current_turn_rules_v2",
        "router_reason": reason,
        "router_scope": scope,
    }


def _detect_on_text(text: str, scope: str) -> Optional[SceneResult]:
    t = _norm(text)
    if not t:
        return None


    # Phase 7.9.7：补充真实语料中高频但容易 unknown 的短业务问题。
    if re.search(r"(几天到|几天能到|多久到|多久能到|大概几天|到[^，。！？]*几天)", t):
        return _mk("logistics_policy", 210, ["几天到"], "命中到达时效/运输时效咨询", scope)

    if re.search(r"(怎么下单|单怎么下|怎么拍|拍几份|拍几件|怎么付款|提交订单|修改数量|加入购物车|立即购买)", t):
        return _mk("order_modify_policy", 209, ["下单/拍单"], "命中下单方式/拍单/数量修改咨询", scope)

    if re.search(r"(少放油|少放|不要放发货单|不要发货单|备注一下|帮我备注|留言备注)", t):
        return _mk("order_modify_policy", 208, ["备注/特殊要求"], "命中订单备注/特殊要求", scope)

    if re.search(r"([5-9][0-9]|[1-9][0-9]{2,})(支|个|件|包|盒|份|斤|套|把|条|箱)", t) and re.search(r"(多久|几天|需要多久|一般需要多久|多长时间)", t):
        return _mk("bulk_purchase_policy", 207, ["大数量+多久"], "命中大单/定制工期咨询", scope)

    # 0. 明确当前轮：包装要求属于发货前处理/备注，先接住，避免被质量问题抢走。
    packaging_hits = _hits(t, ["包装严实", "包装好", "包好点", "包好一点", "寄之前包装", "发货前检查", "不要放发货单"])
    if packaging_hits:
        return _mk("shipping_policy", 206 + len(packaging_hits), packaging_hits, "命中发货前包装/发货单处理要求", scope)

    # 1. 描述不符/售前承诺不一致。排除普通发货承诺。
    desc = _hits(t, ["描述不符", "页面写", "详情页", "图片上", "你们说", "客服说", "不是说", "和说的不一样", "页面上都写", "假的"])
    shipping_words = _hits(t, ["今天发", "明天发", "发货", "没发", "什么时候发", "多久发"])
    if desc and not shipping_words:
        return _mk("description_mismatch", 204 + len(desc), desc, "命中页面描述/历史承诺不一致", scope)

    # 2. 强投诉。
    complaint_strong = _hits(t, ["投诉", "差评", "骗人", "不讲道理", "不靠谱", "假的", "太过分", "什么态度", "废话", "痕死"])
    complaint_soft = _hits(t, ["无语", "太慢", "搞什么", "不相信", "等了几天", "问你们几天"])
    if complaint_strong or (scope != "full_context" and complaint_soft):
        hs = complaint_strong + complaint_soft
        return _mk("complaint_policy", 202 + len(hs), hs, "命中投诉/强不满表达", scope)

    # 3. 发票。
    hs = _hits(t, ["发票", "开票", "收据", "抬头", "税号", "纳税人", "增值税", "专票", "普票", "报销"])
    if hs:
        return _mk("invoice_policy", 200 + len(hs), hs, "命中发票/开票/抬头/税号咨询", scope)

    # 4. 发货时效。
    shipping_time_hits = _hits(t, [
        "什么时候发货", "什么时候发", "今天发货", "今天能发货", "明天发货", "明天能发",
        "多久发货", "多久能发", "几天发货", "还没发货", "迟迟不发", "已付款请查看今天能发货吗",
        "付款了今天能发", "现在拍什么时候发货", "什么时候可以发", "啥时候发", "何时发货",
        "48小时", "72小时", "发出了吗", "还没发", "尽快发货", "加急发货"
    ])
    if shipping_time_hits:
        return _mk("shipping_policy", 198 + len(shipping_time_hits), shipping_time_hits, "命中发货时效/催发货", scope)

    # 5. 快递方式。若当前句同时包含 carrier 和“备注”，carrier 优先，因为用户指定的是快递方式备注。
    express_specific_hits = _hits(t, [
        "发什么快递", "什么快递", "哪家快递", "寄哪家", "默认快递", "快递方式",
        "发顺丰", "用顺丰", "走顺丰", "顺丰到付", "顺丰加", "发中通", "发圆通", "发申通",
        "发韵达", "发百世", "发邮政", "发EMS", "指定快递"
    ])
    carrier_hits = _hits(t, ["申通", "中通", "圆通", "韵达", "百世", "汇通", "天天", "邮政", "EMS", "顺丰"])
    logistics_problem_hits = _hits(t, ["物流", "签收", "没收到", "没有收到", "驿站", "派件", "揽收", "单号", "退回", "丢", "催快递", "停了", "运输"])
    shipping_time_noise = _hits(t, ["什么时候", "今天", "明天", "多久", "几天", "发货", "发出"])
    if express_specific_hits or (carrier_hits and not logistics_problem_hits and not shipping_time_noise):
        hs = express_specific_hits + carrier_hits
        return _mk("express_policy", 196 + len(hs), hs, "命中快递方式/指定快递咨询", scope)

    # 6. 优惠券。加强“优惠券/优惠劵/开抢/领券/减25”等真实表达。
    coupon_hits = _hits(t, [
        "优惠券", "购物券", "领券", "领取优惠券", "券用不了", "不能用券", "用不了券", "抵扣不了",
        "满减券", "抢券", "开抢", "开始领", "不能领取", "没有到两点", "满50减25", "减25", "券在哪里", "链接领取"
    ])
    if coupon_hits or ("券" in t and _hits(t, ["领", "用", "减", "抵扣", "抢", "领取", "开抢"])):
        hs = coupon_hits or ["券"]
        return _mk("coupon_policy", 194 + len(hs), hs, "命中优惠券领取/使用/抢券问题", scope)

    # 7. 普通优惠/活动/改价。
    promo_hits = _hits(t, ["优惠", "便宜", "少点", "活动", "满减", "买一送一", "买二送一", "聚划算", "改价", "最低价", "特价", "划算", "买多优惠", "再优惠", "价格"])
    if promo_hits:
        return _mk("promotion_policy", 192 + len(promo_hits), promo_hits, "命中普通优惠/活动/改价咨询", scope)

    # 8. 运费/包邮。
    fee_hits = _hits(t, ["包邮", "运费", "邮费", "快递费", "免运费", "补邮", "到付"])
    if fee_hits:
        return _mk("shipping_fee_policy", 190 + len(fee_hits), fee_hits, "命中包邮/运费/邮费问题", scope)

    # 9. 赠品/试吃/礼袋。补充真实表达：不送、没有送、没送、多送。
    gift_hits = _hits(t, [
        "赠品", "送什么", "送不送", "有没有送", "试吃", "核桃夹", "夹子", "湿巾", "开口器",
        "礼品袋", "礼袋", "多送", "不送", "没有送", "没送", "送了呗", "送多", "单片湿巾"
    ])
    # 如果是“少送/漏发”，后面 missing 会接；但若明确是赠品名，比如湿巾/礼袋，按赠品问题处理。
    if gift_hits and _hits(t, ["湿巾", "礼品袋", "礼袋", "赠品", "试吃", "夹子", "开口器", "多送", "不送"]):
        return _mk("gift_policy", 188 + len(gift_hits), gift_hits, "命中赠品/试吃/随单赠送问题", scope)

    # 10. 少件/漏发。真实少件优先于普通物流，但如果是“快递弄丢/催快递”则交给 logistics。
    logistics_lost = _hits(t, ["快递的问题", "帮我催催快递", "催快递", "快递弄丢", "他们弄丢"])
    if logistics_lost:
        return _mk("logistics_policy", 187 + len(logistics_lost), logistics_lost, "命中快递丢失/催快递问题", scope)

    missing_hits = _hits(t, ["少件", "漏发", "少发", "少了", "少送", "没放", "没有放", "缺件", "东西少", "少了很多"])
    if missing_hits:
        return _mk("missing_package_policy", 186 + len(missing_hits), missing_hits, "命中少件/漏发/少送问题", scope)

    # 11. 物流异常/进度。
    hs = _hits(t, ["物流", "签收", "没收到", "没有收到", "揽收", "派件", "驿站", "快递员", "单号", "运输途中", "站点", "退回", "拒收", "包裹", "快递慢", "停那么久", "怎么那么慢", "催快递", "拦回来"])
    if hs:
        return _mk("logistics_policy", 184 + len(hs), hs, "命中物流进度/签收/拒收/单号问题", scope)

    # 12. 退款。
    refund_hits = _hits(t, ["退款", "退钱", "返钱", "返款", "退到哪里", "多久到账", "申请退款", "取消订单", "仅退款"])
    if refund_hits:
        return _mk("refund_policy", 182 + len(refund_hits), refund_hits, "命中退款/取消订单/到账问题", scope)

    # 13. 退换货。
    return_hits = _hits(t, ["退货", "换货", "退换", "寄回", "退回来", "7天无理由", "能退吗", "可以退吗", "退一款", "退一份", "退23包", "申请已收到货"])
    if return_hits:
        return _mk("return_exchange", 180 + len(return_hits), return_hits, "命中退换货/寄回/无理由售后问题", scope)

    # 14. 价保/差价。当前句或最近上下文明确“差价”时才走。
    price_hits = _hits(t, ["差价", "补差价", "返差价", "退差价", "降价", "涨价", "价保", "买贵了"])
    if price_hits:
        return _mk("price_protection", 178 + len(price_hits), price_hits, "命中价保/差价/降价涨价问题", scope)

    # 15. 订单修改。
    order_modify_hits = _hits(t, ["改地址", "地址改", "地址错", "地址不对", "改电话", "电话少", "备注", "拍错", "发错", "不要发错", "换成", "帮我改", "改一下"])
    if order_modify_hits:
        return _mk("order_modify_policy", 176 + len(order_modify_hits), order_modify_hits, "命中订单信息修改/备注/拍错调整", scope)

    # 16. 库存/预售/到货。避免“收到货啦”被当库存。
    stock_hits = _hits(t, ["有货", "没货", "缺货", "什么时候有货", "什么时候到货", "预售", "下架", "到新货", "库存", "补货", "新货吗"])
    if stock_hits:
        return _mk("stock_policy", 174 + len(stock_hits), stock_hits, "命中库存/预售/到货时间咨询", scope)

    # 17. 批发/大量采购/定制大单。注意“买多送”更偏活动/赠品，不强行 bulk。
    bulk_hits = _hits(t, ["批发", "大量", "团购", "买几十", "100支", "200支", "100个", "200个", "几百", "定制", "起订", "刻字"])
    if bulk_hits:
        return _mk("bulk_purchase_policy", 172 + len(bulk_hits), bulk_hits, "命中批发/大量购买/定制大单咨询", scope)

    # 18. 商品参数/口味/颜色/材质。
    product_hits = _hits(t, [
        "尺寸", "多大", "材质", "纯棉", "无纺布", "颜色", "红色", "黑色", "口味", "味道", "好吃",
        "甜", "咸", "奶油", "椒盐", "原味", "软", "硬", "厚", "薄", "吸水", "生产日期", "保质期",
        "配料", "成分", "荧光", "干湿两用", "盖子", "规格", "型号", "一包多少", "多少克", "花纹",
        "礼盒", "绿色", "二合一", "一体", "茶刀", "茶针", "红木", "黑木", "檀"
    ])
    if product_hits:
        return _mk("product_qa_policy", 170 + len(product_hits), product_hits, "命中商品参数/口味/材质/尺寸咨询", scope)

    # 19. 质量问题。
    quality_hits = _hits(t, ["坏了", "坏的", "破了", "漏了", "出油", "味道差", "质量问题", "不好吃", "不吸水", "瑕疵", "裂痕", "坏果", "变质", "发酸", "酸了", "不能用", "不会坏"])
    if quality_hits:
        return _mk("quality_issue", 168 + len(quality_hits), quality_hits, "命中商品质量/损坏/变质问题", scope)

    return None


def detect_current_turn_scene_v2(route_query: str) -> Optional[SceneResult]:
    user_turns = _extract_user_turns(route_query)
    last_user = user_turns[-1] if user_turns else _norm(route_query)
    recent = _extract_recent_text(route_query, recent_lines=4)
    full = _norm(route_query)

    # 1. 当前轮强意图。
    current_hit = _detect_on_text(last_user, scope="current_turn")
    if current_hit:
        current_hit["last_user_query"] = last_user
        return current_hit

    # 2. 低信息当前句才依赖最近上下文。
    if _is_low_info(last_user):
        recent_hit = _detect_on_text(recent, scope="recent_context")
        if recent_hit:
            recent_hit["last_user_query"] = last_user
            return recent_hit

    # 3. 非低信息但当前轮没命中，保守看最近上下文。
    recent_hit = _detect_on_text(recent, scope="recent_context")
    if recent_hit:
        recent_hit["last_user_query"] = last_user
        return recent_hit

    # 4. 全文兜底。
    full_hit = _detect_on_text(full, scope="full_context")
    if full_hit:
        full_hit["last_user_query"] = last_user
        return full_hit

    return None


def route_with_current_turn_rules_v2(route_query: str, base_retriever: Callable[[str], SceneResult]) -> SceneResult:
    hit = detect_current_turn_scene_v2(route_query)
    if hit:
        return hit

    base = base_retriever(route_query)
    if isinstance(base, dict):
        base.setdefault("router_source", "base_retrieve_policy_auto")
        base.setdefault("router_scope", "base")
    return base
