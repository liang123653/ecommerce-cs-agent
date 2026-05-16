# 电商智能客服 Agent 项目简历与面试讲解稿

## 1. 简历项目名称

电商智能客服 Agent 原型｜RAG + 业务路由 + 多轮记忆 + 风险控制

## 2. 简历项目描述

构建了一个面向电商售前、售中、售后场景的可控客服 Agent 原型，系统不是简单依赖 LLM 自由生成回复，而是通过业务场景路由、SOP/RAG 检索、订单/商品/物流/售后事实查询、多轮历史记忆和安全规则校验，生成可控、可追溯、可回归评测的客服回复。

系统支持价格保护、退换货、物流异常、发货时效、商品质量问题、退款到账和投诉等典型客服场景，并针对“历史承诺冲突、商品描述不符、售后争议”等高风险多轮对话引入 context-aware fallback，在 LLM 策略分类前读取历史上下文，避免模型忽略历史沟通或直接给出不安全承诺。

## 3. 简历 Bullet 版本

- 设计并实现电商客服 Agent 主链路，覆盖用户输入、业务策略路由、SOP/RAG 检索、订单/商品/物流/售后事实注入、LLM 回复生成、规则校验与安全兜底。
- 构建多轮上下文记忆能力，支持每轮对话后写入 `conversation_messages`，下一轮基于 `user_id/conversation_id` 召回历史消息，并在高风险历史上下文下触发受控 fallback。
- 实现 `context-aware fallback v2` 与 pre-strategy high-risk fast path，使历史承诺冲突、商品属性争议、售后纠纷等场景可在 LLM 分类前被拦截，降低不安全回复风险。
- 建立可回归评测体系，包括 15 条 clean business pipeline eval、30 条 seeded multiturn gold smoke、runtime memory write/read smoke 与 FastAPI multiturn API smoke。
- 在开启 memory read/write、context fallback 与 fast path 后，clean business pipeline 达到 scene/file/rule/safety/overall 100%；30 条多轮 gold 中安全率 100%，行为通过率 96.67%。
- 验证 SFT/DPO 数据与训练链路，完成 pairwise DPO LoRA smoke，但基于安全与回归稳定性考虑，主链路暂未上线 adapter，采用 base model + RAG + fact tools + guardrails 的可控方案。

## 4. 面试 1 分钟介绍

这个项目是我做的一个电商智能客服 Agent，不是普通聊天机器人。普通 LLM 在客服场景里容易乱承诺，比如直接说可以退款、可以补偿、可以发货，或者在多轮对话里忘记前面客服说过什么。

所以我把系统拆成了几个可控模块：先做业务场景路由，再做 SOP/RAG 检索，同时接入订单、商品、物流、售后这些结构化事实，最后让 LLM 在这些上下文里生成回复，并通过规则校验和 fallback 做安全控制。

后面我重点增强了多轮记忆能力。系统会在每轮对话后把用户和客服消息写入 memory，下一轮根据 user_id 和 conversation_id 召回历史。如果发现用户当前问题和历史答复存在冲突，比如“你们之前说支持，结果收到没有”，系统会在 LLM 策略分类前触发 context-aware fallback，避免忽略历史或给出不安全承诺。

目前这个项目已经有 FastAPI `/chat` demo，可以真实跑两轮对话：第一轮写入 memory，第二轮读取历史并触发高风险 fallback。评测上，15 条 clean business pipeline 达到 overall 100%，30 条多轮 gold 安全率 100%，行为通过率 96.67%。

## 5. 面试 3 分钟讲解

这个项目的核心目标是解决 LLM 在真实客服场景中的三个问题：第一是事实不可靠，第二是业务规则不可控，第三是多轮历史容易被忽略。

因此我没有把它设计成“用户问一句，模型答一句”的自由生成系统，而是做成一个受控 Agent 主链路。

整体流程是：

```text
用户输入
  -> answer strategy 路由
  -> SOP / RAG 检索
  -> 订单 / 商品 / 物流 / 售后事实查询
  -> 历史对话 memory 检索
  -> LLM 回复生成
  -> 规则校验 / fallback
  -> 写入 conversation memory

在业务能力上，系统支持价格保护、退换货、发货时效、物流异常、质量问题、退款到账和投诉等客服高频场景。每个场景不会只靠关键词判断，而是结合 SOP 检索、结构化事实和最终规则校验。

我后面重点做的是多轮上下文能力。最初的问题是，很多早退分支比如低信息、常识、商品知识类问题，会绕过 memory，导致用户说“你们之前说过”的时候，系统还是给泛化回复。为了解决这个问题，我做了 context-aware fallback v2：当系统发现当前用户有历史对话，并且历史中存在潜在承诺、商品属性答复或争议风险时，会直接返回一个安全的上下文承接回复，而不是继续走普通早退模板。

同时我加了 pre-strategy fast path。也就是说，高风险历史上下文可以在 LLM 策略分类前就被拦截，避免分类模型把它误判成 common sense 或 product knowledge。

在 memory write 方面，我没有直接把写库逻辑硬塞进核心策略函数，而是做了一个 wrapper：answer_with_strategy_and_memory_write。它先调用原来的主链路生成回复，再根据 feature flag 写入 conversation_messages。这样既能验证真实多轮，也不会破坏原始主链路。

最后我把它接成 FastAPI demo。POST /chat 会调用带 memory write 的主链路，POST /debug/history 可以检查某个用户当前问题能否召回历史。API smoke 里第一轮写入 memory，第二轮读取历史后触发 CONTEXT_AWARE_FALLBACK，证明这是一个真实可运行的多轮 Agent，而不是提前 seed 的假测试。

评测方面，我做了几组回归：

15 条 clean business pipeline：scene_acc、file_acc、rule_hit_rate、safety_rate、overall_rate 都是 100%；
30 条 seeded multiturn gold：safe_reply_rate 100%，behavior_pass_rate 96.67%；
runtime memory write/read smoke：written=True，has_history=True，fallback=True；
FastAPI API smoke：两轮 /chat 能写入、召回并触发高风险 fallback。

这个项目里我也尝试了 SFT/DPO 链路，包括 pairwise DPO 数据构造和 LoRA smoke 训练，但最终没有直接上线 adapter。原因是客服场景里安全和事实一致性优先，adapter 必须经过 base vs adapter 回归对比，确认稳定提升后才能上线。这也是我在项目里体现工程决策的一点：不是所有训练结果都应该直接接入生产链路。

6. 面试官可能追问
Q1：你这个项目和普通 RAG 客服机器人有什么区别？

普通 RAG 通常是“检索文档 + LLM 回答”，但我的系统多了业务控制层和多轮风险控制。

区别主要有三点：

不是所有问题都直接 RAG，而是先做 answer strategy 路由；
回复不只依赖文档，还结合订单、商品、物流、售后等结构化事实；
多轮对话中会读取历史，并对历史承诺冲突或争议表达做高风险 fallback。

所以它更像一个受控业务 Agent，而不是普通知识库问答。

Q2：为什么不直接用微调模型？

因为客服场景最重要的是安全和事实一致性。微调可以改善表达风格，但不能保证模型不会乱承诺。

我在项目里验证了 SFT/DPO 链路，但主链路仍然优先采用 base model + RAG + fact tools + guardrails。adapter 只有在通过 base-vs-adapter 回归评测后才会上线。

Q3：多轮记忆怎么做的？

我把每轮用户和客服消息写入 conversation_messages，下一轮根据 user_id、conversation_id 和当前 query 检索相关历史。检索结果会形成 history_context，里面包括 has_history、risk_level、messages 等字段。

如果 risk_level 是 high，或者历史 summary 里有高风险标签，就会触发 context-aware fallback。

Q4：为什么要做 context-aware fallback？

因为客服场景里很多风险来自历史上下文。例如用户说“你们之前说可以退”“你们之前说支持这个功能”，这类问题如果只看当前句子，可能会被误判成普通售后或商品咨询。

context-aware fallback 的作用是：在未核实前不直接承诺退款、补偿、发货或认责，而是引导用户提供订单号、截图、实物照片，并转人工或售后继续核实。

Q5：评测怎么做？

我做了三类评测：

clean business pipeline eval：验证原有业务链路是否被破坏；
multiturn gold smoke：验证多轮上下文行为是否符合预期；
API smoke：验证真实 /chat 接口能完成写入 memory、读取历史和触发 fallback。
Q6：现在项目还有什么不足？

主要有三点：

conversation_summaries 自动更新还可以增强；
真实客服日志的大规模 no-hit / low-score 聚类闭环还可以继续做；
SFT/DPO adapter 还没有完成系统性 base-vs-adapter 对比。

但目前作为简历和面试 demo，核心主链路、多轮记忆、API demo 和评测证据已经完整。

7. 项目亮点总结
不是单纯套 LLM，而是业务可控 Agent 主链路；
有 SOP/RAG，也有订单、商品、物流、售后结构化事实；
有多轮 memory read/write；
有高风险历史上下文 fallback；
有 FastAPI demo；
有 clean eval、多轮 gold、API smoke 三类证据；
有训练链路探索，但没有盲目上线 adapter，体现工程取舍。
8. 可以写进简历的一句话

构建电商智能客服 Agent 原型，基于 RAG/SOP 检索、订单与售后事实工具、多轮 memory guard 和规则安全兜底，实现可控客服回复生成；支持 runtime memory write/read 与 FastAPI 多轮 demo，在 clean business pipeline 上达到 overall/safety 100%，在 30 条多轮 gold smoke 上达到 safety 100%、behavior 96.67%。
