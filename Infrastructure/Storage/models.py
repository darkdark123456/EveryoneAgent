"""
models.py

数据库表定义
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from Infrastructure.Storage.database import (
    Base
)


class User(Base):
    """
    用户表
    """
    
    __tablename__ = "users"

    # 用户ID
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    # 邮箱
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    # 用户名
    username: Mapped[str] = mapped_column(
        String(100)
    )

    # 加密后的密码
    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    # 创建时间
    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow
        )
    )
    
    

class Conversation(Base):
    """
    会话表
    """

    __tablename__ = "conversations"

    # 会话ID
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    # 所属用户
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    # 会话标题
    title: Mapped[str] = mapped_column(
        String(255)
    )

    # 创建时间
    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow
        )
    )

    # 更新时间
    updated_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow
        )
    )

    # 软删除
    is_deleted: Mapped[bool] = (
        mapped_column(
            default=False
        )
    )
    
    messages = relationship(
    "Message",
    backref="conversation"
)

class Message(Base):
    """
    消息表
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    conversation_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "conversations.id"
            )
        )
    )

    role: Mapped[str] = mapped_column(
        String(50)
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            default=datetime.utcnow
        )
    )
    
    
class UserMemory(Base):

    __tablename__ = "user_memories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True  
    )

    memory_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    #memory type
    memory_key: Mapped[str] = mapped_column(
        String,
        nullable=True
    )

    # content text
    memory_value: Mapped[str] = mapped_column(
        String,
        nullable=True
    )

    # importance level
    importance: Mapped[int] = mapped_column(
        Integer,
        default=1
    )
    
    access_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=True
    )

    last_access_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )
    
    # updated time
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    
    score: Mapped[float] = mapped_column(
        default=0.0,
        nullable=True
    )
    
    
    
    
class ConversationSummary(Base):

    __tablename__ = "conversation_summary"

    id = Column(
        Integer,
        primary_key=True
    )

    conversation_id = Column(
        Integer,
        unique=True
    )

    #当前摘要
    summary = Column(
        Text,
        default=""
    )
    
    #上次摘要的消息数目
    last_message_count = Column(
        Integer,
        default=0
    )
    
    
    
    
class MemoryGraph(Base):

    __tablename__ = "memory_graph"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer
    )

    source: Mapped[str] = mapped_column(
        String
    )

    relation: Mapped[str] = mapped_column(
        String
    )

    target: Mapped[str] = mapped_column(
        String
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    
    
class ReflectionMemory(Base):

    __tablename__ = "reflection_memory"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    reflection_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.5
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    
class ReflectionState(Base):

    __tablename__ = "reflection_state"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    conversation_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False
    )

    last_reflection_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    



class Goal(Base):

    __tablename__ = "goals"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    goal: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    goal_type: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    status: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    
    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    
    importance: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=1
    )
    
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        default=0.5
    )
    
    
    last_reflection_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    update_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )