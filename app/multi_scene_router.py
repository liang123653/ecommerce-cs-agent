from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "config" / "scene_schema_phase8.json"


CHAR_MAP = str.maketrans({
    "劵": "券",
    "優": "优",
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


def normalize_text(text: str) -> str:
    text = (text or "").translate(CHAR_MAP)
    text = text.replace("优惠劵", "优惠券")
    text = text.replace("為什麼", "为什么")
    text = text.replace("為什么", "为什么")
    return re.sub(r"\s+", "", text)


def extract_user_turns(route_query: str) -> List[str]:
    turns: List[str] = []
    for line in (route_query or "").splitlines():
        line = line.strip()
        if line.startswith("用户："):
            turns.append(normalize_text(line.split("用户：", 1)[1]))
    if not turns and route_query:
        turns.append(normalize_text(route_query))
    return [t for t in turns if t]


def extract_recent_context(route_query: str, recent_lines: int = 4) -> str:
    lines = [x.strip() for x in (route_query or "").splitlines() if x.strip()]
    return normalize_text("\n".join(lines[-recent_lines:]))


@dataclass
class SceneScore:
    scene: str
    file_name: str
    score: float
    priority: int
    hits: List[str]
    negative_hits: List[str]
    description: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scene": self.scene,
            "file_name": self.file_name,
            "score": round(self.score, 4),
            "priority": self.priority,
            "hits": self.hits,
            "negative_hits": self.negative_hits,
            "description": self.description,
        }


class MultiSceneRouter:
    """
    Phase 8 config-driven router.

    核心变化：
    1. 规则集中在 config/scene_schema_phase8.json；
    2. 输出 top_k 多候选场景，不再只靠 if/elif 单标签；
    3. 当前轮权重大于上下文，减少旧话题污染；
    4. priority 只用于同分/近似同分时的业务优先级。
    """

    def __init__(self, schema_path: Optional[str | Path] = None):
        self.schema_path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
        self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        self.weights = self.schema.get("global", {}).get(
            "weights",
            {"current_turn": 6, "recent_context": 2, "full_context": 1},
        )
        self.low_info_words = set(self.schema.get("global", {}).get("low_info_words", []))
        self.meaningful_hints = self.schema.get("global", {}).get("meaningful_hints", [])
        self.scenes = self.schema.get("scenes", [])

    def is_low_info(self, text: str) -> bool:
        t = normalize_text(text)
        if not t:
            return True
        if t in self.low_info_words:
            return True
        if any(h in t for h in self.meaningful_hints):
            return False
        if len(t) <= 2:
            return True
        if re.fullmatch(r"[0-9]+", t):
            return True
        return False

    def _keyword_hits(self, text: str, keywords: List[str]) -> List[str]:
        t = normalize_text(text)
        return [kw for kw in keywords if kw and kw in t]

    def _regex_hits(self, text: str, patterns: List[str]) -> List[str]:
        t = normalize_text(text)
        hits: List[str] = []
        for pat in patterns or []:
            try:
                if re.search(pat, t):
                    hits.append(pat)
            except re.error:
                continue
        return hits

    def _score_scene(self, scene_cfg: Dict[str, Any], current: str, recent: str, full: str) -> SceneScore:
        scene = scene_cfg["scene"]
        file_name = scene_cfg["file_name"]
        priority = int(scene_cfg.get("priority", 0))
        description = scene_cfg.get("description", "")

        positive = scene_cfg.get("positive_keywords", [])
        negative = scene_cfg.get("negative_keywords", [])
        patterns = scene_cfg.get("regex_patterns", [])

        parts = [
            ("current_turn", current, self.weights.get("current_turn", 6)),
            ("recent_context", recent, self.weights.get("recent_context", 2)),
            ("full_context", full, self.weights.get("full_context", 1)),
        ]

        score = 0.0
        hits: List[str] = []
        negative_hits: List[str] = []

        for _, text, weight in parts:
            kh = self._keyword_hits(text, positive)
            rh = self._regex_hits(text, patterns)
            nh = self._keyword_hits(text, negative)

            if kh:
                score += weight * len(kh)
                hits.extend(kh)
            if rh:
                score += weight * 2 * len(rh)
                hits.extend([f"re:{x}" for x in rh])
            if nh:
                score -= weight * len(nh)
                negative_hits.extend(nh)

        # priority 是弱加成，避免规则数量多的场景天然压制高风险场景
        if score > 0:
            score += priority / 100.0

        return SceneScore(
            scene=scene,
            file_name=file_name,
            score=score,
            priority=priority,
            hits=sorted(set(hits), key=hits.index),
            negative_hits=sorted(set(negative_hits), key=negative_hits.index),
            description=description,
        )

    def route(self, route_query: str, top_k: int = 5) -> Dict[str, Any]:
        user_turns = extract_user_turns(route_query)
        current = user_turns[-1] if user_turns else normalize_text(route_query)
        recent = extract_recent_context(route_query)
        full = normalize_text(route_query)

        if self.is_low_info(current):
            return {
                "scene": "unknown",
                "file_name": "unknown_policy.md",
                "score": 0,
                "router_source": "phase8_multi_scene_router",
                "router_reason": "low_info_current_turn",
                "current_turn": current,
                "candidate_scenes": [],
            }

        scored = [
            self._score_scene(scene_cfg, current=current, recent=recent, full=full)
            for scene_cfg in self.scenes
        ]

        scored = [s for s in scored if s.score > 0]
        scored.sort(key=lambda x: (x.score, x.priority), reverse=True)

        if not scored:
            return {
                "scene": "unknown",
                "file_name": "unknown_policy.md",
                "score": 0,
                "router_source": "phase8_multi_scene_router",
                "router_reason": "no_scene_score",
                "current_turn": current,
                "candidate_scenes": [],
            }

        primary = scored[0]
        return {
            "scene": primary.scene,
            "file_name": primary.file_name,
            "score": round(primary.score, 4),
            "hits": primary.hits,
            "negative_hits": primary.negative_hits,
            "router_source": "phase8_multi_scene_router",
            "router_reason": "config_weighted_multiscene_score",
            "current_turn": current,
            "candidate_scenes": [x.as_dict() for x in scored[:top_k]],
        }


_ROUTER: Optional[MultiSceneRouter] = None


def get_multiscene_router() -> MultiSceneRouter:
    global _ROUTER
    if _ROUTER is None:
        _ROUTER = MultiSceneRouter()
    return _ROUTER


def route_with_multiscene_router(route_query: str, top_k: int = 5) -> Dict[str, Any]:
    return get_multiscene_router().route(route_query, top_k=top_k)
