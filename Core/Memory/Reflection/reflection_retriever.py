import json

from sqlalchemy.orm import Session
from Infrastructure.Storage.models import ReflectionMemory



class ReflectionRetriever:
    TOP_K: int = 5
    @staticmethod
    def get_top_reflections(
        db: Session,
        user_id: int,
        limit: int=5
    )->  list[ReflectionMemory]:
        return (
        db.query(
            ReflectionMemory
        )
        .filter(
            ReflectionMemory.user_id
            ==
            user_id
        )
        .order_by(
            ReflectionMemory.importance.desc(),
            ReflectionMemory.created_at.desc()
        )
        .limit(limit)
        .all()
    )