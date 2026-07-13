from typing import List, Tuple

from Core.Planner.planner_executor import PlannerExecutor, ToolResult
from Core.Planner.planner_models import PlannerResult
from Core.Planner.planner_service import PlannerService


class PlannerManager:
    @classmethod
    async def run(
        cls,
        query: str,
    ) -> Tuple[list[PlannerResult], List[ToolResult]]:
        plan: list[PlannerResult] = await PlannerService.generate_plan(
            query
    )
        
        tool_results: List[ToolResult] = (
            await PlannerExecutor.execute_plan(
                plan
            )
        )
        
        return plan, tool_results