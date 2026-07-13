"""
chat.py

聊天相关模型
"""

from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    用户聊天请求
    """
    conversation_id: int
    message: str
    
    
class ChatResponse(BaseModel):
    """
    Agent回复
    """

    response: str