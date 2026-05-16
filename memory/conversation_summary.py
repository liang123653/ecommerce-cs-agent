from typing import List, Dict, Any


def build_history_prompt_section(history_context: Dict[str, Any]) -> str:
    """
    把历史检索结果转换成适合注入 prompt 的文本。
    """
    if not history_context or not history_context.get('has_history'):
        return '未检索到相关历史对话。'

    return (
        f"历史风险等级：{history_context.get('risk_level')}\n"
        f"风险原因：{history_context.get('risk_reason')}\n\n"
        f"{history_context.get('summary')}"
    )


def summarize_messages_rule_based(messages: List[Dict[str, Any]]) -> str:
    """
    本地规则版摘要器。
    后续可以替换成 LLM 摘要。
    """
    if not messages:
        return '无历史消息。'

    user_msgs = [m['content'] for m in messages if m.get('role') == 'user']
    assistant_msgs = [m['content'] for m in messages if m.get('role') == 'assistant']

    parts = []
    if user_msgs:
        parts.append(f"用户历史咨询：{'；'.join(user_msgs[:3])}")
    if assistant_msgs:
        parts.append(f"历史客服回复：{'；'.join(assistant_msgs[:3])}")

    return '\n'.join(parts)
