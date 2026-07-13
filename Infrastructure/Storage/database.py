"""database.py 数据库连接管理模块
负责：
1. 创建数据库引擎
2. 创建Session工厂
3. 提供数据库会话
4. 提供ORM基类
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker
)
from sqlalchemy.engine import Engine

# ==================================================
# SQLite数据库文件
# ==================================================

DATABASE_URL: str = (
    "sqlite:///agent.db"
)


# ==================================================
# 创建数据库引擎
# ==================================================
#
# 引擎可以理解成：
#
# Python
#    ↓
# Engine
#    ↓
# SQLite
#
# 所有数据库操作最终都会经过它
#
# ==================================================

engine: Engine = create_engine(

    DATABASE_URL,

    connect_args={
        # SQLite特殊配置
        # 允许多线程访问
        "check_same_thread": False
    }

)


# ==================================================
# Session工厂
# ==================================================
#
# Session相当于：
#
# 数据库连接对象
#
# 后面：
#
# db = SessionLocal()
#
# 就能获得数据库连接
#
# ==================================================

SessionLocal = sessionmaker(

    bind=engine,

    autocommit=False,

    autoflush=False

)


# ==================================================
# ORM基类
# ==================================================
#
# 所有数据库表都继承它
#
# User
# Conversation
# Message
#
# ==================================================

class Base(DeclarativeBase):
    """
    ORM基类
    """
    pass

# ==================================================
# 获取数据库Session
# ==================================================
#
# FastAPI依赖注入会使用它
#
# ==================================================

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    Returns:
        Generator[Session]
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()