"""memeory对外统一接口"""
"""
记忆管理器
"""

from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from Core.Memory.KV.memory_chat import (
    convert_messages
)

from Infrastructure.Storage.models import (
    Message
)

from Core.Memory.KV.memory_service import (
    get_messages_by_conversation
)


def load_memory(
    db: Session,
    conversation_id: int
)-> list[BaseMessage]:
    """
    加载历史记忆
    """

    db_messages: list[Message] = (
        get_messages_by_conversation(
            db,
            conversation_id
        )
    )

    return convert_messages(
        db_messages
    )