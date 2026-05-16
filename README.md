# Ecommerce Customer Service Agent

一个面向电商售前 / 售中 / 售后场景的可控客服 Agent 原型。

本项目不是简单的自由聊天机器人，而是围绕真实客服业务构建的：

```text
RAG + SOP + 订单事实 + 商品事实 + 多轮记忆 + 风险控制 + 评测回归
1. 项目目标

在电商客服场景中，LLM 直接生成回复容易出现以下问题：

忽略平台规则；
编造退款、补偿、发货承诺；
忽略订单 / 售后状态；
多轮对话中忘记历史沟通；
对投诉、描述不符、质量问题等高风险场景回复不稳。

本项目的目标是构建一个 可控、可评测、可回归 的客服 Agent 主链路。

2. 核心链路
用户输入
  -> 策略路由 answer_strategy
  -> SOP / RAG 检索
  -> 订单 / 商品 / 物流 / 售后事实查询
  -> 历史对话 memory 检索
  -> LLM 生成客服回复
  -> 规则校验 / 安全兜底
  -> 写入 conversation memory
3. 已实现能力
业务能力
价格保护咨询
退换货咨询
发货时效咨询
物流异常咨询
商品质量问题
退款到账咨询
投诉与高风险表达处理
Agent 能力
SOP / RAG 检索
订单事实注入
商品事实注入
多轮历史记忆读取
多轮消息写入
高风险历史上下文识别
context-aware fallback v2
FastAPI /chat demo
/debug/history 历史召回检查接口
4. 多轮记忆能力

系统支持真实多轮：

第 1 轮 /chat
  -> 生成回复
  -> 写入 conversation_messages

第 2 轮 /chat
  -> 根据 user_id / conversation_id 读取历史
  -> 判断历史风险
  -> 必要时触发 CONTEXT_AWARE_FALLBACK

示例：

用户第 1 轮：这个耳机支持主动降噪吗？
系统：暂未查到准确商品事实，请提供商品链接或截图核实。

用户第 2 轮：你们之前说支持主动降噪，结果收到后根本没有，怎么办？
系统：触发高风险历史上下文 fallback，引导上传订单号、页面截图和实物照片，并转人工或售后核实。
5. FastAPI Demo

启动服务：

USE_CONVERSATION_MEMORY=1 \
USE_CONVERSATION_MEMORY_WRITE=1 \
USE_CONTEXT_AWARE_FALLBACK=1 \
USE_CONTEXT_AWARE_FALLBACK_FAST=1 \
PYTHONPATH=. uvicorn app.api_chat:app --host 0.0.0.0 --port 8002

健康检查：

curl -s http://127.0.0.1:8002/health | python -m json.tool

运行多轮 API smoke：

HOST=http://127.0.0.1:8002 bash eval/smoke_api_chat_multiturn.sh
6. 评测结果
Clean Business Pipeline

在开启 memory read、memory write、context fallback、fast path 后：

total: 15
scene_acc: 100%
file_acc: 100%
rule_hit_rate: 100%
safety_rate: 100%
overall_rate: 100%
fallback_rate: 6.67%
Multiturn Gold Smoke

30 条 seeded multiturn gold：

runtime_success_rate: 100%
safe_reply_rate: 100%
behavior_pass_rate: 96.67%
API Multiturn Smoke

两轮 API 测试通过：

Turn 1 memory_write.written = true
/debug/history has_history = true
/debug/history risk_level = high
Turn 2 strategy = CONTEXT_AWARE_FALLBACK
Turn 2 context_fallback_used = true
Turn 2 memory_write.written = true
7. SFT / DPO 状态

项目中已验证：

SFT 数据格式方向；
DPO pairwise 数据构造；
LLaMA-Factory DPO LoRA smoke 训练；
adapter 可保存。

但当前主链路暂未启用 SFT / DPO adapter。

原因：

在客服业务场景中，安全和事实一致性优先。
训练 adapter 必须经过 base vs adapter 回归对比后才能上线。

当前线上 demo 采用：

Base Qwen + RAG + SOP + fact tools + guardrails
8. 工程决策

本项目避免通过不断补关键词或业务词表来解决真实客服问题。

核心思路是：

硬过滤
  + 上下文检索 query 构造
  + SOP / fact 检索
  + no-hit / low-score 聚类
  + 人工 cluster 决策
  + SOP 回流
  + 主链路回归评测
9. 当前项目状态

按简历 / 面试 demo 标准：

完成度：约 85%

已完成：

主链路可运行；
clean eval 100%；
多轮 memory guard 已接入；
runtime memory write 已验证；
FastAPI demo 已接入；
API 多轮 smoke 已通过。

后续可扩展：

conversation_summaries 自动更新；
更大规模真实客服 replay；
no-hit / low-score 聚类；
base vs SFT vs DPO 效果对比；
前端 demo 页面。
