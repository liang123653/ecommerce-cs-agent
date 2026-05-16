import json
import math
import os
import re
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT_DIR / "rag" / "index"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

DOMAIN_PHRASES = [
    "价保", "差价", "补差价", "降价", "退差价",
    "退货", "换货", "七天无理由", "二次销售", "吊牌", "包装", "试穿", "清洗",
    "发货", "催发货", "待发货", "出库", "仓库", "调拨",
    "物流", "快递", "签收", "没收到", "驿站", "代收", "派送", "丢件",
    "退款", "到账", "原路退回", "支付渠道",
    "质量问题", "售后", "照片", "视频", "维修", "瑕疵", "坏了", "破损", "开胶", "裂痕", "无法使用",
    "投诉", "差评", "骗人", "生气", "客服",
]

SCENE_FILE_MAP = {
    "price_protection": "price_protection.md",
    "return_exchange": "return_exchange.md",
    "shipping_policy": "shipping_policy.md",
    "logistics_policy": "logistics_policy.md",
    "refund_policy": "refund_policy.md",
    "quality_issue": "quality_issue.md",
    "complaint_policy": "complaint_policy.md",
}

SCENE_KEYWORDS = {
    "price_protection": ["降价", "价保", "补差价", "退差价", "买贵", "价格变低", "便宜"],
    "return_exchange": ["退货", "换货", "不合适", "尺码", "吊牌", "穿过", "洗过", "试穿", "颜色不喜欢", "二次销售"],
    "shipping_policy": ["发货", "待发货", "催发", "什么时候发", "出库", "急用", "仓库", "调拨"],
    "logistics_policy": ["物流", "快递", "签收", "没收到", "派送", "驿站", "丢件", "不动", "代收"],
    "refund_policy": ["退款", "到账", "钱", "退到哪里", "原路退回"],
    "quality_issue": ["质量", "坏", "坏了", "破", "破损", "开胶", "裂", "裂痕", "瑕疵", "不能用", "无法使用", "污渍", "售后", "维修"],
    "complaint_policy": ["投诉", "骗人", "差评", "生气", "无语", "客服不处理", "服务差"],
}

# 场景优先级：当 query 同时命中多个场景时，高风险售后/质量/物流优先
SCENE_PRIORITY = {
    "quality_issue": 7,
    "logistics_policy": 6,
    "price_protection": 5,
    "refund_policy": 4,
    "shipping_policy": 3,
    "return_exchange": 2,
    "complaint_policy": 1,
}


def detect_keyword_scene(query: str) -> tuple[str | None, dict]:
    scores = {}
    for scene, keywords in SCENE_KEYWORDS.items():
        hit_count = sum(1 for kw in keywords if kw in query)
        if hit_count > 0:
            scores[scene] = hit_count

    if not scores:
        return None, {}

    best_scene = max(
        scores.keys(),
        key=lambda s: (scores[s], SCENE_PRIORITY.get(s, 0))
    )
    return best_scene, scores


def tokenize_zh(text: str):
    text = text.lower()
    tokens = []

    for phrase in DOMAIN_PHRASES:
        if phrase.lower() in text:
            tokens.append(phrase.lower())

    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    joined = "".join(chinese_chars)

    for n in (2, 3):
        for i in range(max(0, len(joined) - n + 1)):
            tokens.append(joined[i:i+n])

    tokens.extend(re.findall(r"[a-zA-Z0-9_]+", text))
    return tokens


def normalize_sparse(vec: dict):
    norm = math.sqrt(sum(v * v for v in vec.values()))
    if norm == 0:
        return vec
    return {k: v / norm for k, v in vec.items()}


def sparse_dot(a: dict, b: dict):
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


class TfidfRetriever:
    def __init__(self):
        index_path = INDEX_DIR / "kb_tfidf.json"
        if not index_path.exists():
            raise FileNotFoundError(
                "离线 TF-IDF 索引不存在，请先运行：\n"
                "PYTHONPATH=. python rag/build_vector_index.py --backend tfidf"
            )

        payload = json.loads(index_path.read_text(encoding="utf-8"))
        self.chunks = payload["chunks"]
        self.idf = payload["idf"]
        self.doc_vectors = payload["doc_vectors"]

    def search(self, query: str, top_k: int = 8):
        tokens = tokenize_zh(query)
        tf = Counter(tokens)
        query_vec = {
            token: count * self.idf.get(token, 0.0)
            for token, count in tf.items()
            if token in self.idf
        }
        query_vec = normalize_sparse(query_vec)

        scored = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            scored.append((sparse_dot(query_vec, doc_vec), idx))

        scored.sort(reverse=True, key=lambda x: x[0])

        results = []
        for score, idx in scored[:top_k]:
            chunk = self.chunks[idx]
            results.append({
                "score": float(score),
                "file_name": chunk["file_name"],
                "title": chunk["title"],
                "content": chunk["content"],
            })

        return results


class BgeFaissRetriever:
    def __init__(self, model_name_or_path: str | None = None):
        import faiss
        from sentence_transformers import SentenceTransformer

        index_path = INDEX_DIR / "kb.faiss"
        meta_path = INDEX_DIR / "kb_meta.json"

        if not index_path.exists() or not meta_path.exists():
            raise FileNotFoundError(
                "BGE/FAISS 向量索引不存在，请先运行：\n"
                "PYTHONPATH=. python rag/build_vector_index.py --backend bge --embedding_model <本地模型路径>"
            )

        self.index = faiss.read_index(str(index_path))
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        self.chunks = metadata["chunks"]
        self.model_name_or_path = (
            model_name_or_path
            or os.getenv("EMBEDDING_MODEL_PATH")
            or metadata.get("embedding_model")
            or DEFAULT_EMBEDDING_MODEL
        )

        print(f"加载 embedding 模型: {self.model_name_or_path}")
        self.model = SentenceTransformer(self.model_name_or_path)

    def search(self, query: str, top_k: int = 8):
        query_emb = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(query_emb, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunk = self.chunks[int(idx)]
            results.append({
                "score": float(score),
                "file_name": chunk["file_name"],
                "title": chunk["title"],
                "content": chunk["content"],
            })

        return results


_vector_retriever = None


def get_vector_retriever():
    global _vector_retriever
    if _vector_retriever is not None:
        return _vector_retriever

    backend = os.getenv("VECTOR_RAG_BACKEND", "auto")

    if backend == "tfidf":
        _vector_retriever = TfidfRetriever()
    elif backend == "bge":
        _vector_retriever = BgeFaissRetriever()
    else:
        if (INDEX_DIR / "kb_tfidf.json").exists():
            _vector_retriever = TfidfRetriever()
        elif (INDEX_DIR / "kb.faiss").exists():
            _vector_retriever = BgeFaissRetriever()
        else:
            raise FileNotFoundError(
                "没有可用向量索引。请先运行：\n"
                "PYTHONPATH=. python rag/build_vector_index.py --backend tfidf"
            )

    return _vector_retriever


def hybrid_rerank(query: str, chunks: list[dict], top_k: int = 3):
    """
    Hybrid RAG 重排：
    1. 先用 BGE/TF-IDF 做语义召回；
    2. 再用客服业务关键词判断强意图；
    3. 对强意图对应 SOP 文件加权，避免“商品坏了”被误分到普通退换货。
    """
    keyword_scene, keyword_scores = detect_keyword_scene(query)
    target_file = SCENE_FILE_MAP.get(keyword_scene) if keyword_scene else None

    reranked = []
    for rank, chunk in enumerate(chunks):
        base_score = float(chunk["score"])
        bonus = 0.0

        # 越靠前的原始向量结果保留一点排序优势
        rank_bonus = max(0.0, 0.03 - rank * 0.005)

        # 强关键词场景加权
        if target_file and chunk["file_name"] == target_file:
            bonus += 0.12

        # 质量问题特殊规则：坏了/开胶/破损/无法使用 + 售后，强制优先 quality_issue
        quality_strong_words = ["坏", "坏了", "破损", "开胶", "裂痕", "无法使用", "质量", "瑕疵"]
        if any(w in query for w in quality_strong_words) and chunk["file_name"] == "quality_issue.md":
            bonus += 0.18

        # 价保特殊规则
        if any(w in query for w in ["降价", "价保", "补差价", "退差价"]) and chunk["file_name"] == "price_protection.md":
            bonus += 0.16

        # 签收未收到特殊规则
        if "签收" in query and "没收到" in query and chunk["file_name"] == "logistics_policy.md":
            bonus += 0.16

        # 穿过/洗过特殊规则
        if any(w in query for w in ["穿过", "洗过", "试穿", "吊牌"]) and chunk["file_name"] == "return_exchange.md":
            bonus += 0.16

        final_score = base_score + bonus + rank_bonus
        new_chunk = dict(chunk)
        new_chunk["raw_score"] = base_score
        new_chunk["score"] = final_score
        new_chunk["rerank_bonus"] = bonus + rank_bonus
        reranked.append(new_chunk)

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked[:top_k], keyword_scene, keyword_scores


def retrieve_policy_vector(query: str, top_k: int = 3):
    retriever = get_vector_retriever()

    # 先多召回一些，再做 hybrid rerank
    raw_chunks = retriever.search(query, top_k=max(8, top_k))
    chunks, keyword_scene, keyword_scores = hybrid_rerank(query, raw_chunks, top_k=top_k)

    if not chunks:
        return {
            "scene": "unknown",
            "file_name": "",
            "content": "",
            "chunks": [],
            "keyword_scene": keyword_scene,
            "keyword_scores": keyword_scores,
        }

    top_file = chunks[0]["file_name"]
    scene = top_file.replace(".md", "")

    content = "\n\n---\n\n".join(
        f"【来源文件】{c['file_name']}\n【重排后分数】{c['score']:.4f}\n【原始分数】{c.get('raw_score', c['score']):.4f}\n{c['content']}"
        for c in chunks
    )

    scene_map = {
        "price_protection": "price_protection",
        "return_exchange": "return_exchange",
        "shipping_policy": "shipping_policy",
        "logistics_policy": "logistics_policy",
        "refund_policy": "refund_policy",
        "quality_issue": "quality_issue",
        "complaint_policy": "complaint_policy",
    }

    return {
        "scene": scene_map.get(scene, scene),
        "file_name": top_file,
        "content": content,
        "chunks": chunks,
        "keyword_scene": keyword_scene,
        "keyword_scores": keyword_scores,
    }
