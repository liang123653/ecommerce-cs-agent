import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


ROOT_DIR = Path(__file__).resolve().parents[1]
KB_DIR = ROOT_DIR / "knowledge_base"
INDEX_DIR = ROOT_DIR / "rag" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"


def split_markdown(text: str, file_name: str):
    """
    简单 Markdown 切分：
    - 按二级标题/段落切分
    - 保留文件名和片段内容
    """
    chunks = []
    current_title = ""
    buffer = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            current_title = stripped.lstrip("#").strip()
            continue

        if stripped.startswith("## "):
            if buffer:
                content = "\n".join(buffer).strip()
                if content:
                    chunks.append({
                        "file_name": file_name,
                        "title": current_title,
                        "content": content,
                    })
                buffer = []
            buffer.append(stripped)
        else:
            buffer.append(line)

    if buffer:
        content = "\n".join(buffer).strip()
        if content:
            chunks.append({
                "file_name": file_name,
                "title": current_title,
                "content": content,
            })

    return chunks


def load_chunks():
    chunks = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(split_markdown(text, path.name))
    return chunks


def normalize_embeddings(embeddings: np.ndarray):
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.clip(norms, 1e-12, None)


def build_index(model_name_or_path: str = DEFAULT_EMBEDDING_MODEL):
    print(f"加载 embedding 模型: {model_name_or_path}")
    model = SentenceTransformer(model_name_or_path)

    chunks = load_chunks()
    texts = [
        f"文件：{c['file_name']}\n标题：{c['title']}\n内容：{c['content']}"
        for c in chunks
    ]

    print(f"知识片段数量: {len(texts)}")
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "kb.faiss"))

    metadata = {
        "embedding_model": model_name_or_path,
        "chunks": chunks,
    }
    (INDEX_DIR / "kb_meta.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"向量索引已保存: {INDEX_DIR / 'kb.faiss'}")
    print(f"元数据已保存: {INDEX_DIR / 'kb_meta.json'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--embedding_model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Embedding 模型名称或本地路径，例如 /home/host/ljy/model/bge-small-zh-v1.5",
    )
    args = parser.parse_args()

    build_index(args.embedding_model)
