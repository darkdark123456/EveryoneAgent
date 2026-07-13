from datetime import datetime


from math import exp
from datetime import datetime

from Infrastructure.Storage.models import UserMemory


class MemoryRanker:
    LAMBDA: float = 0.005
    @classmethod
    def score(
        cls,
        memory: UserMemory
    ) -> float:

        """重要程度"""
        importance_score: float = (
            memory.importance / 10
        )

        """访问次数"""
        access_score: float = (

            min(
                memory.access_count,
                1000
            )

            / 1000
        )

        """基础得分"""
        base_score: float = (

            0.7 * importance_score

            +

            0.3 * access_score
        )

        """过去天数"""
        days: int = (

            datetime.utcnow()

            -

            memory.last_access_time

        ).days

        """最终得分"""
        final_score: float = (

            base_score

            *

            exp(
                -cls.LAMBDA * days
            )
        )

        return final_score