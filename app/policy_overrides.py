from pathlib import Path
from typing import Dict, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
KB_DIR = ROOT_DIR / "knowledge_base"


DESCRIPTION_SOURCE_WORDS = [
    "页面写", "详情页写", "商品写", "宣传说", "标的是",
    "你们说", "你们之前说", "之前说", "客服说", "当时说", "不是说",
    "说好了", "承诺", "介绍说",
]

MISMATCH_WORDS = [
    "不一致", "不符合", "不是", "没有", "根本没有", "没有这个",
    "不能用", "用不了", "不支持", "不行", "不对", "和说的不一样",
    "和页面不一样", "描述不符", "虚假宣传", "骗我", "骗人",
]

# 如果明确是这些业务，不要强行改成描述不符
EXCLUDED_SCENE_HINTS = [
    "发货", "物流", "快递", "签收", "退款", "到账",
    "价保", "补差价", "发票", "开票", "优惠券", "满减",
]


def _load_policy_file(file_name: str) -> str:
    path = KB_DIR / file_name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _build_forced_policy(
    file_name: str,
    scene: str,
    reason: str,
    original_policy: Dict[str, Any],
) -> Dict[str, Any]:
    content = _load_policy_file(file_name)
    return {
        "scene": scene,
        "file_name": file_name,
        "content": (
            f"【策略修正原因】{reason}\n"
            f"【来源文件】{file_name}\n"
            f"{content}"
        ),
        "chunks": [
            {
                "file_name": file_name,
                "title": "policy_override",
                "content": content,
                "score": 1.0,
                "raw_score": original_policy.get("chunks", [{}])[0].get("score", 0.0) if original_policy.get("chunks") else 0.0,
                "rerank_bonus": 1.0,
                "override_reason": reason,
            }
        ],
        "keyword_scene": scene,
        "keyword_scores": {scene: 1},
        "override_applied": True,
        "override_reason": reason,
        "original_scene": original_policy.get("scene"),
        "original_file_name": original_policy.get("file_name"),
    }


def looks_like_description_mismatch(query: str) -> bool:
    """
    判断是否属于“商品描述不符 / 售前承诺不一致”。

    重点不是识别具体属性词，而是识别通用语义模式：
    描述来源/历史承诺 + 实际不一致表达。

    这样可以覆盖食品、服饰、数码、虚拟权益等不同商品类目，
    不需要枚举所有商品属性。
    """
    if any(w in query for w in EXCLUDED_SCENE_HINTS):
        # 避免“之前说今天发货”“之前说退款到账”等被误判为商品描述不符
        # 这些应该交给发货/退款/物流/发票/优惠等对应场景。
        non_product_dispute = any(w in query for w in ["发货", "物流", "快递", "签收", "退款", "到账", "发票", "开票", "优惠券", "满减"])
        if non_product_dispute:
            return False

    has_source = any(w in query for w in DESCRIPTION_SOURCE_WORDS)
    has_mismatch = any(w in query for w in MISMATCH_WORDS)

    if has_source and has_mismatch:
        return True

    # 用户直接使用“描述不符/虚假宣传”等强表达，也归入该场景
    if any(w in query for w in ["描述不符", "虚假宣传", "和页面不一样", "和说的不一样"]):
        return True

    return False


def apply_policy_overrides(user_query: str, policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    对 RAG 输出做业务后处理。

    作用：
    - 修正少数 RAG 误召回；
    - 将“商品描述不符/售前承诺不一致”统一路由到 description_mismatch。
    """
    scene = policy.get("scene")

    if looks_like_description_mismatch(user_query) and scene != "description_mismatch":
        return _build_forced_policy(
            file_name="description_mismatch_policy.md",
            scene="description_mismatch",
            reason="当前问题疑似商品描述不符或售前承诺不一致，优先按描述不符高风险售后场景处理",
            original_policy=policy,
        )

    return policy
