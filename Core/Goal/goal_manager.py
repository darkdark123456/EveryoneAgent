from sqlalchemy.orm import Session

from Core.Goal.goal_models import GoalResult
from Core.Goal.goal_service import (
    GoalService
)


from Core.Memory.Reflection.reflection_retriever import ReflectionRetriever
from Core.Planner.planner_manager import PlannerManager
from Infrastructure.Storage.crud import (
    get_active_goal,
    get_graph_memories,
    get_last_goal_reflection_count,
    get_reflection_count,
    get_reflection_state,
    get_summary,
    save_goal,
    update_goal
)


from sqlalchemy.orm import Session

from Core.Goal.goal_service import (
    GoalService
)

from Infrastructure.Storage.crud import (
    get_active_goal,
    save_goal,
    update_goal
)
from Infrastructure.Storage.models import ConversationSummary, Goal, MemoryGraph, ReflectionMemory, ReflectionState


class GoalManager:
    GOAL_TRIGGER: int = 3
    @classmethod
    async def check_and_update_goal(
        cls,
        db: Session,
        user_id: int,
        conversation_id: int
    ) -> None:


        """获得反思次数"""
        state:ReflectionState | None = get_reflection_state(db=db,conversation_id=conversation_id)
        
        reflection_count: int= (
            state.last_reflection_count
            if state
            else 0
        )
        
        
        last_goal_reflection_count: int = (
          await  get_last_goal_reflection_count(
                db,
                user_id
            )
        ) # type: ignore

        
        
        if (

            reflection_count

            -

            last_goal_reflection_count

            <

            cls.GOAL_TRIGGER
        ):
            return
                

        """获得会话摘要"""
        summary_text: str = "[user conversation summary] is "
        summary: ConversationSummary | None =get_summary(
            db=db,
            conversation_id=conversation_id
        )
        
        if summary is not None:
            summary_text +=summary.summary # type: ignore
        else:
            summary_text += "null"

        
        """获得会话知识图谱"""
        graph_text: str = "[user conversation graph] is "
        graphs_relations: list[MemoryGraph] | None=get_graph_memories(db=db,user_id=user_id)
        
        if graphs_relations is not None:
            for relation in graphs_relations:
                graph_text += ("source: "+str(relation.source)+" relation: "+str(relation.relation)+" target: "+str(relation.target)+" importance: "+str(relation.importance)+"\n")
        else:
            graph_text += "null"
        
        
        """获得会话反思"""
        reflection_text: str = "[user reflection] is "
        reflections: list[ReflectionMemory] = (
            ReflectionRetriever.get_top_reflections(
                db,
                user_id
            )
        )
        
        
        if reflections is not None:
            for reflection in reflections:
                reflection_text += "reflection content: "+str(reflection.content)+" importance: "+str(reflection.importance)+" reflection type: "+str(reflection.reflection_type)+" confidence: "+str(reflection.confidence)+"\n"
        else:
            reflection_text += "null"
        
        """生成目标"""
        goal_result: GoalResult = (
            await GoalService.generate_goal(
                summary_text=summary_text,
                graph_text=graph_text,
                reflection_text=reflection_text
            )
        )

        """从数据库中获得活着的最重要的目标"""
        current_goal: Goal | None = (
           await get_active_goal(
                db,
                user_id
            )
        )

        
        if current_goal is None:
            await save_goal(
                db=db,
                user_id=user_id,
                goal_result=goal_result,
                reflection_count=reflection_count
            )
            return

            
        """如果目标标题相同,更新目标"""
        if (
            current_goal.title
            ==
            goal_result.title
        ):

            await update_goal(
                db=db,
                goal_id=current_goal.id,
                confidence=goal_result.confidence,
                importance=goal_result.importance,
                description=goal_result.description,
                reflection_count=reflection_count
                
            )

            return

        """如果目标标题不同,完成当前目标,创建新目标"""
        current_goal.status = "completed"
        
        db.commit()
        
        await save_goal(
            db=db,
            user_id=user_id,
            goal_result=goal_result,
            reflection_count=reflection_count
        )
        

        
    @classmethod
    async def _get_active_goals(cls, db: Session, user_id: int) -> Goal | None: # type: ignore
        return await get_active_goal(db=db, user_id=user_id)

