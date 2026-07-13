"""记忆数据库存储"""
from sqlalchemy.orm import Session
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from Infrastructure.Storage.models import (
    Message
)

from sqlalchemy.orm import Session

from Infrastructure.Storage.crud import (
    get_messages_by_conversation,
    _update_memory_by_importance,
)


from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage
)

from Infrastructure.Storage.models import (
    UserMemory
)

from Core.Memory.KV.memory_extractor import MemoryExtractor,MemoryItem
    
    
def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    保存消息
    """

    message: Message = Message(

        conversation_id=conversation_id,

        role=role,

        content=content
    )

    db.add(message)

    db.commit()

    db.refresh(message)

    return message


def load_messages(
    db: Session,
    conversation_id: int
) -> list[BaseMessage]:
    """
    从数据库恢复历史消息
    """
    records: list[Message] = (

        get_messages_by_conversation(
            db=db,
            conversation_id=conversation_id
        )
    )
    history: list[BaseMessage] = []
    for record in records:
        if record.role == "用户":

            history.append(

                HumanMessage(
                    content=record.content
                )
            )

        elif record.role == "E-Agent":

            history.append(

                AIMessage(
                    content=record.content
                )
            )

    return history



def save_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    content: str
) -> UserMemory:
    """
    保存长期记忆
    """
    memory: UserMemory = UserMemory(

        user_id=user_id,

        memory_type=memory_type,

        content=content
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory



def get_memories(
    db: Session,
    user_id: int
) -> list[UserMemory]:
    """
    获取用户长期记忆
    """

    return (

        db.query(UserMemory)

        .filter(
            UserMemory.user_id
            ==
            user_id
        )

        .all()
    )
    


def build_memory_prompt(
    memories: list[UserMemory]
) -> str:

    if not memories:

        return ""

    memory_text = "\n".join(

        memory.content

        for memory in memories
    )

    return f"""
用户长期记忆：

{memory_text}

请结合以上信息回答问题。
"""


def _save_memory_by_importance(
    db: Session,
    user_id: int,
    memory_type: str,
    content: str,
    key: str,
    value: str,
    importance_level: int
)-> None:
    _update_memory_by_importance(
        db=db,
        user_id=user_id,
        memory_type=memory_type,
        key=(key if key is not None else ""),
        value=(value if value is not None else ""),
        importance=importance_level
    )
    
