from sqlalchemy.orm import Session

from Infrastructure.Storage.crud import get_message_top_k
from Infrastructure.Storage.models import Message


class MessageMemoryService:
    TOP_K: int = 5
    def __init__(self) -> None:
        pass
    @classmethod
    async def build_prompt(cls,db:Session,conversation_id:int,top_k:int=5) -> str:
        prompt: str=""
        
        messages:list[Message] =await cls.get_messages_top(db=db,conversation_id=conversation_id) # type: ignore
        for message in messages:
            prompt += f"{message.role}:{message.content}\n"
        return prompt
        
    @classmethod
    async def get_messages_top(cls,db:Session,conversation_id:int) -> list[Message]:
        """最近topk会话记录prompt"""
        message_top_k: list[Message] = await get_message_top_k(db=db,conversation_id=conversation_id,top_k=cls.TOP_K)
        return message_top_k
    
    