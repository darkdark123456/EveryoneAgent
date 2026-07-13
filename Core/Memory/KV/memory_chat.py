"""记忆实现"""
"""
聊天记忆工具
"""

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage
)

def convert_messages(
    db_messages: list
) -> list[BaseMessage]:
    """
    数据库消息转换成LangGraph消息
    """

    result: list[BaseMessage] = []

    for msg in db_messages:

        if msg.role == "user":

            result.append(

                HumanMessage(
                    content=msg.content
                )
            )

        elif msg.role == "assistant":

            result.append(

                AIMessage(
                    content=msg.content
                )
            )

    return result