import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import os
import streamlit as st
from app.pipeline import answer as answer_rule
from app.pipeline_llm import answer_with_llm


st.set_page_config(page_title="中文电商智能客服 Demo - Qwen版", page_icon="🛒", layout="wide")

st.title("🛒 中文电商智能客服大模型落地系统")
st.caption("Phase 3：关键词检索 / 向量 RAG + 业务工具查询 + Qwen 润色 + 规则校验兜底")

with st.sidebar:
    st.header("运行模式")
    mode = st.radio(
        "选择回复生成方式：",
        ["规则模板回复", "本地 Qwen 回复"],
        index=1,
    )

    rag_mode = st.radio(
        "知识检索方式：",
        ["关键词检索", "向量 RAG"],
        index=0,
    )

    os.environ["USE_VECTOR_RAG"] = "1" if rag_mode == "向量 RAG" else "0"

    st.header("示例问题")
    examples = [
        "订单 202604240001 怎么还没发货？",
        "订单 202604240002 物流显示签收但我没收到",
        "订单 202604240003 刚买就降价了怎么办？",
        "订单 202604240004 商品有质量问题怎么处理？",
        "我穿了一次还能退吗？",
        "衣服不合适可以退吗？",
    ]
    selected = st.radio("选择一个示例：", examples)

query = st.text_area("请输入用户问题：", value=selected, height=100)

if st.button("生成客服回复", type="primary"):
    with st.spinner("正在检索 SOP、查询业务数据并生成回复..."):
        if mode == "本地 Qwen 回复":
            result = answer_with_llm(query)
        else:
            result = answer_rule(query)
            result["retriever"] = "keyword"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("客服回复")
        st.write(result["reply"])

        st.subheader("识别结果")
        display = {
            "order_id": result["order_id"],
            "scene": result["scene"],
            "policy_file": result["policy_file"],
            "mode": mode,
            "retriever": result.get("retriever", "keyword"),
        }
        if "fallback_used" in result:
            display["fallback_used"] = result["fallback_used"]
            display["validation_errors"] = result["validation_errors"]
        st.json(display)

    with col2:
        st.subheader("业务数据查询结果")
        st.json(result["business_context"])

    if result.get("retrieved_chunks"):
        with st.expander("查看向量召回片段"):
            for i, chunk in enumerate(result["retrieved_chunks"], 1):
                st.markdown(f"### Top {i} | {chunk['file_name']} | score={chunk['score']:.4f}")
                st.markdown(chunk["content"])

    with st.expander("查看命中的 SOP 知识"):
        st.markdown(result["retrieved_policy"])

    if "reference_reply" in result:
        with st.expander("查看规则参考回复"):
            st.write(result["reference_reply"])

    if "llm_reply" in result:
        with st.expander("查看 Qwen 原始回复"):
            st.write(result["llm_reply"])

    if "messages" in result:
        with st.expander("查看发送给大模型的 Prompt"):
            st.json(result["messages"])
