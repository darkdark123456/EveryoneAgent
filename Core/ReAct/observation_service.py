from langchain_core.messages import AIMessage
from mcp.types import CallToolResult

from Core.Agent.agent_factory import AgentFactory
from Core.Planner.planner_executor import ToolResult
from Core.ReAct.observation_prompt import (
    OBSERVATION_PROMPT
)
from Infrastructure.Configs.Configuration import Configuration
from langchain_community.chat_models import ChatTongyi

class ObservationService:
    @classmethod
    async def _get_llm_model(cls) -> ChatTongyi:
        return await AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()
    
    @classmethod
    async def generate_answer(
        cls,
        question: str,
        thought: str,
        observation: str
    ) -> str:

        llm: ChatTongyi = await cls._get_llm_model()

        prompt: str = OBSERVATION_PROMPT.format(

            question=question,

            thought=thought,

            observation=observation
        )

        result: AIMessage = (
            await llm.ainvoke(
                [
                    (
                        "user",
                        prompt
                    )
                ]
            )
        )

        return str(
            result.content.strip() # type: ignore
        )
    @staticmethod
    async def extract_observation(
            result: CallToolResult
        ) -> str:

        if not result.content:

            return ""

        return "\n".join(

            item.text # type: ignore
            for item in result.content
        )