import json
from string import Template
from typing import Tuple
from Core.Agent.agent_factory import AgentFactory
from Core.Agent.agent_model import AgentType
from Core.Agent.agent_prompt import AGENT_ROUTER_PROMPT, get_agent_plan_route_prompt
from Infrastructure.Configs.Configuration import Configuration
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage, UsageMetadata


class AgentRouterService:
    input_token: int = 0
    output_token: int = 0
    total_token: int = 0
    @staticmethod
    async def get_token_use()->Tuple[int,int,int]:
        return AgentRouterService.input_token,AgentRouterService.output_token,AgentRouterService.total_token
    @staticmethod
    async def get_llm_model() -> ChatTongyi:
        return await AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()
    @classmethod
    async def route(
        cls,
        query:str
    ) ->  list[dict[str,str]]:

        llm: ChatTongyi = await AgentRouterService.get_llm_model()

        messages: list = [
            (
                "system",
                AGENT_ROUTER_PROMPT
            ),
            (
                "human",
                query
            )
        ]

        response: AIMessage = await llm.ainvoke(messages)

        meta: dict=response.response_metadata
        usage: UsageMetadata | None = meta.get("token_usage", {})
        assert usage is not None
        
        AgentRouterService.input_token+=usage.get("input_tokens",0)
        AgentRouterService.output_token+=usage.get("output_tokens",0)
        AgentRouterService.total_token+=usage.get("total_tokens",0)

        data: list[dict[str,str]] = json.loads(response.content) # type: ignore

        return data
    @staticmethod
    async def format_agent_referebce(
       plan: str
    ) -> str:
        plan_agent_reference_prompt: Template =await get_agent_plan_route_prompt()
        format_prompt = plan_agent_reference_prompt.substitute(plan=plan)
        return format_prompt
    
    @classmethod
    async def get_plann_agent_reference(
        cls,
        plan:str
    ) ->  list[dict[str,str]]:

        llm: ChatTongyi = await AgentRouterService.get_llm_model()
        plan_agent_reference_prompt: str =await cls.format_agent_referebce(plan)
        
        messages: list = [
            (
                "system",
                plan_agent_reference_prompt
                        
            )

        ]
        
        response: AIMessage = await llm.ainvoke(messages)

        meta: dict=response.response_metadata
        usage: UsageMetadata | None = meta.get("token_usage", {})
        assert usage is not None
        
        AgentRouterService.input_token+=usage.get("input_tokens",0)
        AgentRouterService.output_token+=usage.get("output_tokens",0)
        AgentRouterService.total_token+=usage.get("total_tokens",0)

        data: list[dict[str,str]] = json.loads(response.content) # type: ignore

        return data