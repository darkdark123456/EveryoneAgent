from typing import Any

from Capability.MCP.mcp_registry import MCPRegistry
import json
from langchain_core.messages import AIMessage

from Core.Agent.agent_factory import AgentFactory
from Core.ReAct.react_models import (
    ReActResult,
    ToolAction
)

from Core.ReAct.react_prompt import (
    REACT_PROMPT
)

from Infrastructure.Configs.Configuration import Configuration

from langchain_community.chat_models import ChatTongyi

class ReActService:
    @staticmethod
    async def _get_llm_model() -> ChatTongyi:
        return await AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()
    @classmethod
    async def think(
        cls,
        user_query: str
    ) -> ReActResult:

        llm: ChatTongyi = await cls._get_llm_model()

        messages: list = [

            (
                "system",
                REACT_PROMPT
            ),

            (
                "user",
                user_query
            )
        ]
        
        result: AIMessage = (
            await llm.ainvoke(
                messages
            )
        )
        
        raw: str = result.content.strip() # type: ignore
        try:

            json_data: Any = json.loads(raw)

            return ReActResult(
                **json_data
            )

        except Exception:

            return ReActResult(
                thought="解析失败",
                action=ToolAction(tool_name="",arguments={}),
                final_answer="系统错误"
            )