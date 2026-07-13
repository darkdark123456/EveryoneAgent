from Infrastructure.Storage.models import (
    UserMemory
)

from sqlalchemy.orm import Session


class MemoryRetriever:
    @staticmethod
    def get_user_memories(
        db: Session,
        user_id: int,
        min_importance: int = 1
    ) -> list[UserMemory]:
        """
        获取用户全部长期记忆
        """

        return (

            db.query(UserMemory)

            .filter(
                UserMemory.user_id
                ==
                user_id
            )
            .filter(
                UserMemory.importance >= min_importance
            )

            .all()
        )
    @staticmethod
    def get_user_memories_by_importance(
        db: Session,
        user_id: int,
        min_importance: int = 1
    ) -> list[UserMemory]:
        """
        按重要程度由大到小获取用户全部长期记忆
        """
        return (

            db.query(UserMemory)

            .filter(
                UserMemory.user_id
                ==
                user_id
            )

            .order_by(
                
                UserMemory.score.desc()
            )
            .all()
        )
        

        return MemoryRetriever._get_memory_by_importance(db=db, user_id=user_id)
    
    @staticmethod
    def build_memory_prompt(
        memories: list[UserMemory]
    ) -> str:
        if not memories:
            return ""
        memory_lines: list[str] = []
        memory_values: list[str] = []
        for memory in memories:
            memory_lines.append(str(memory.content) if memory.content is not None else "")
            memory_values.append(str(memory.memory_value) if memory.memory_value is not None else "")
    
        memory_text: str = "\n".join(memory_lines)
        memory_value_text: str = "\n".join(memory_values)
  
        full_memory: str = memory_text + "\n" + memory_value_text
        
        return f"""
        以下是用户长期记忆：
        {full_memory}
        回答问题时可以参考这些信息。
        """
    @staticmethod
    def _get_memory_by_importance(
        db: Session,
        user_id: int,
    ) -> list[UserMemory]:
        return (

        db.query(UserMemory)

        .filter(
            UserMemory.user_id
            ==
            user_id
        )

        .order_by(
            UserMemory.importance.desc()
        )
        .all()
    )
