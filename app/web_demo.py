import streamlit as st
import json
from app.pipeline import answer

st.set_page_config(page_title="中文电商智能客服 Demo", page_icon="🛒", layout="wide")

st.title("🛒 中文电商智能客服大模型落地系统")
st.caption("Phase 1 MVP：SOP 检索 + 订单/物流/退款工具查询 + 客服回复生成")

with st.sidebar:
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
    result = answer(query)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("客服回复")
        st.write(result["reply"])

        st.subheader("识别结果")
        st.json({
            "order_id": result["order_id"],
            "scene": result["scene"],
            "policy_file": result["policy_file"],
        })

    with col2:
        st.subheader("业务数据查询结果")
        st.json(result["business_context"])

    with st.expander("查看命中的 SOP 知识"):
        st.markdown(result["retrieved_policy"])
