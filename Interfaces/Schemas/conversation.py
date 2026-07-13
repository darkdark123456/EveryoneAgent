"""
会话相关Schema
"""

from pydantic import (
    BaseModel,
    Field
)


class CreateConversationRequest(
    BaseModel
):
    """
    创建会话请求
    """
    title: str = Field(
        min_length=1,
        max_length=100
    )


class ConversationResponse(
    BaseModel
):
    """
    会话返回模型
    """

    id: int

    title: str

    class Config:

        from_attributes = True
