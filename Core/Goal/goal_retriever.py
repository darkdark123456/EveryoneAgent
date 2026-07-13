from sqlalchemy.orm import Session

from Infrastructure.Storage.crud import (
    get_active_goal
)
from Infrastructure.Storage.models import Goal


class GoalRetriever:
    @staticmethod
    async def get_goal_prompt(
        db: Session,
        user_id: int
    ) -> str:
        goal: Goal | None = (

           await get_active_goal(
                db,
                user_id
            )
        )
        
        if goal is None:

            return ""
        
        return f"""
            当前用户目标：

            标题：
            {goal.title}

            描述：
            {goal.description}

            完成度：
            {goal.progress}%

            重要度：
            {goal.importance}

            请在回答时结合该目标。
            """