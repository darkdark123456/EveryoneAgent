from Core.ReAct.react_executor import ReActExecutor
from Core.ReAct.react_models import ReActResult
from Core.ReAct.react_service import ReActService
from mcp.types import CallToolResult
from Core.Planner.planner_executor import ToolResult
from Core.ReAct.observation_service import ObservationService
class ReActManager:
    @classmethod
    async def run(
        cls,
        user_query: str
    ) -> str:
        react_result: ReActResult = (
            await ReActService.think(
                user_query
            )
    )
        if react_result.action is None:

            return (
                react_result.final_answer
                or ""
            )
            
        tool_result: CallToolResult = (
            await ReActExecutor.execute(
                react_result.action
            )
        )
        
        observation: str = (
         await   ObservationService.extract_observation(
                tool_result
            )
        )
        
        answer: str = (
            await ObservationService.generate_answer(

                question=user_query,

                thought=react_result.thought,

                observation=observation
            )
        )
        
        return answer
        