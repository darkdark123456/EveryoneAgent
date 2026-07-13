import json

from Core.Agent.agent_factory import AgentFactory
from Core.Goal.goal_models import GoalResult
from Infrastructure.Configs.Configuration import Configuration
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage
from Core.Goal.goal_prompt import get_goal_prompt

class GoalService:
    @classmethod
    async def generate_goal(
        cls,
        summary_text: str,
        graph_text: str,
        reflection_text: str
    ) -> GoalResult:
        human_prompt: str = f"""
        Summary:

        {summary_text}

        Graph:

        {graph_text}

        Reflection:

        {reflection_text}
        """
        
        sys_prompt: str=await get_goal_prompt()
        
        llm: ChatTongyi = await GoalService._get_llm_graph_model()
        message: list = [("system", sys_prompt),
                        ("human", human_prompt)]
        
        result: AIMessage = await llm.ainvoke(message)
        
        raw:str=result.content.strip() # type: ignore
        
        try:
            json_data: dict = json.loads(raw)
            return GoalResult(**json_data)
        except Exception:
            return GoalResult(goal_type="",title="",description="",confidence=0.0,importance=0)
        
    @staticmethod
    async def _get_llm_graph_model() -> ChatTongyi:
        return await  AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()  #