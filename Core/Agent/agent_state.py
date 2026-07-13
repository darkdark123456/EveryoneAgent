"""
LangGraph状态定义
"""

from typing import TypedDict

from langchain_core.messages import (
    BaseMessage
)


class AgentState(
    TypedDict
):
    """
    Agent状态

    messages:
        对话历史
    """

    messages: list[BaseMessage]