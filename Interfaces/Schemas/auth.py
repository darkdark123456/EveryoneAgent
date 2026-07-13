"""
auth.py

认证相关数据模型
"""

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

class RegisterRequest(BaseModel):
    """
    注册请求模型
    """

    email: EmailStr

    username: str = Field(
        min_length=2,
        max_length=50
    )

    password: str = Field(
        min_length=6,
        max_length=100
    )
    
class LoginRequest(BaseModel):
    """
    登录请求模型
    """

    email: EmailStr

    password: str
    
class UserResponse(BaseModel):
    """
    用户响应模型
    """

    id: int

    email: str

    username: str

    class Config:
        from_attributes = True