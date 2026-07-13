from datetime import datetime
from Core.Memory.KV.memory_ranker import MemoryRanker
from Infrastructure.Storage.models import UserMemory
from sqlalchemy.orm import Session



"""记忆清理器"""
class MemoryCleaner:
    FORGET_SCORE: float = 0.05
    MIN_SURVIVAL_DAYS: int = 30
    TRIGGER: int = 7
    @classmethod
    def should_forget(
        cls,
        memory: UserMemory
    ) -> bool:
        
        """如果记忆的重要程度大于等于触发值,不会被忘记"""
        if memory.importance >= cls.TRIGGER:
            return False
        
        """如果记忆的更新时间大于等于最小存活天数,不会被忘记"""
        days_alive: int = (

            datetime.utcnow()

            -

            memory.updated_at

        ).days
        
        if days_alive < cls.MIN_SURVIVAL_DAYS:
            return False
        
        """如果记忆的重要程度小于忘记值,会被忘记"""
        score:float = MemoryRanker.score(
            memory
        )
        
        return score < cls.FORGET_SCORE
    @classmethod
    def cleanup_user_memories(
        cls,
        db: Session,
        user_id: int
    ):
        
        
        memories: list[UserMemory] = (

        db.query(UserMemory)

        .filter(
            UserMemory.user_id
            ==
            user_id
        )

        .all()
        )
        
        """清理记忆"""
        deleted_count: int = 0
        for memory in memories:
            if cls.should_forget(memory):
                db.delete(memory)
                deleted_count += 1
        db.commit()
        return deleted_count
            
        
    
    
    