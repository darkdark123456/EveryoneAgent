from typing import Any, Tuple

from langchain_openai import ChatOpenAI

from Core.Planner.planner_models import PlannerResult
import json

from langchain_core.messages import AIMessage, UsageMetadata

from Core.Planner.planner_models import (
    PlannerResult
)

from Core.Planner.planner_prompt import (
    get_planner_prompt
)

from Capability.MCP.mcp_registry import (
    MCPRegistry
)

from Core.Agent.agent_factory import AgentFactory
from Infrastructure.Configs.Configuration import Configuration
from langchain_community.chat_models import ChatTongyi
from Core.Models.qwen3B_model import QWen3BModel
from Infrastructure.Utils.Logger import SingletonLogger


class PlannerService:
    planner_str: str=""
    input_token:  int=0
    output_token: int=0
    total_token:  int=0
    @staticmethod
    async def get_token_use()->Tuple[int,int,int]:
        return PlannerService.input_token,PlannerService.output_token,PlannerService.total_token
    @staticmethod
    async def _get_llm_graph_model() -> ChatTongyi:
        return await  AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()  #
    @staticmethod
    def build_tool_description() -> str:

        tools = MCPRegistry.get_all_tools()

        result = []

        for tool in tools.values():

            result.append(
                f"""
                工具名称:
                {tool.tool_name}

                工具描述:
                {tool.description}
                """
                        )

        return "\n".join(result)
    @classmethod
    async def generate_plan(
        cls,
        query: str

    ) -> list[PlannerResult]:
        
        planner_result_list: list[PlannerResult] = []
        
        tool_text: str = cls.build_tool_description()
        
        llm: ChatTongyi = await PlannerService._get_llm_graph_model()
        
        #llm: ChatOpenAI =QWen3BModel().llm_local_qwen3B() Docker里面的QWEN3B的 token 只有4096 但是plan的prompt太多了

        sys_prompt: str = get_planner_prompt()
        
        messages: list = [
            ("system", sys_prompt),
            ("human", query),
            ("human", tool_text)
        ]
        
        response: AIMessage = (
            await llm.ainvoke(messages)
        )
        
        meta: dict=response.response_metadata
        usage: UsageMetadata | None = meta.get("token_usage", {})
        assert usage is not None
        
        PlannerService.input_token=usage.get("input_tokens",0)
        PlannerService.output_token=usage.get("output_tokens",0)
        PlannerService.total_token=usage.get("total_tokens",0)

        cls.planner_str = response.content.strip() # type: ignore
        
        
        try:
            json_data = json.loads(cls.planner_str)
            planner_result_list=[PlannerResult(**item) for item in json_data]
            return planner_result_list
        except Exception:
            return [PlannerResult(goal="Unknow", steps=[])]
        
    @classmethod
    async def get_planner_str(cls) -> str:
        return cls.planner_str