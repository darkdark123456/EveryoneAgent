from pathlib import Path
import re
import sys
import json
from typing import Tuple

from langchain_openai import ChatOpenAI

from Core.Agent.agent_factory import AgentFactory
from Infrastructure.Configs.Configuration import Configuration
from Infrastructure.Utils.Logger import SingletonLogger
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from Core.Workflow.workflow_router_type import WorkFlowRouteType
from Core.Workflow.workflow_tools_type  import WorkFlowToolType
from langchain_community.chat_models    import ChatTongyi
from langchain_core.messages            import AIMessage, UsageMetadata
from Core.Models.qwen3B_model           import QWen3BModel



class WorkFlowToolRouter:
    input_token: int = 0
    output_token: int = 0
    total_token: int = 0
    
    _rules: dict = {}
    
    @staticmethod
    async def get_token_use()->Tuple[int,int,int]:
        return WorkFlowToolRouter.input_token,WorkFlowToolRouter.output_token,WorkFlowToolRouter.total_token
    @classmethod
    def _load_rules(cls):

        if cls._rules:
            return

        tool_rulers_path: Path=Path(__file__).parent /"WorkFlowRouterConfig"/"workflow_tools_rulers.json"

        with open(
            tool_rulers_path,
            "r",
            encoding="utf-8"
        ) as f:

            cls._rules = json.load(f)
    @classmethod
    def route(
        cls,
        query: str
    ) -> WorkFlowToolType:

        cls._load_rules()

        query = query.lower()

        for keyword in cls._rules["weather"]:

            if keyword in query:

                return WorkFlowToolType.WEATHER

        for keyword in cls._rules["map"]:

            if keyword in query:

                return WorkFlowToolType.MAP

        for keyword in cls._rules["file"]:

            if keyword in query:

                return WorkFlowToolType.FILE

        for keyword in cls._rules["search"]:

            if keyword in query:

                return WorkFlowToolType.SEARCH

        return WorkFlowToolType.COMMON
    @classmethod
    async def extract_address(
        cls,
        query: str
    ) -> dict:
        WEATHER_ROUTE_PROMPT: str = """
        你是天气工具路由器。
        根据用户的输入,提取地址,如果提取的地址是中文，要先转换为英文。地址使用city字段标识。
        {
            "city":""
        }

        不要解释。
        只输出JSON。
        """
        
        #llm: ChatTongyi=await cls._get_llm_graph_model()
        llm: ChatOpenAI=QWen3BModel().llm_local_qwen3B()
        result: AIMessage = await llm.ainvoke([("system",WEATHER_ROUTE_PROMPT),("human",query)])
        
        usage: UsageMetadata | None = result.usage_metadata
        
        assert usage is not None
        WorkFlowToolRouter.input_token+=usage.get("input_tokens",0)
        WorkFlowToolRouter.output_token+=usage.get("output_tokens",0)
        WorkFlowToolRouter.total_token+=usage.get("total_tokens",0)
        
        content: str = result.content.strip() # type: ignore
        json_match: re.Match[str] | None = re.search(r"\{[\s\S]*?\}", content)
        if not json_match:
            return {"city":""}
        try:
            json_data = json.loads(json_match.group())
            return json_data
        except Exception:
            return {"city":""}
        
    @staticmethod
    async def _get_llm_graph_model() -> ChatTongyi:
        return await  AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()  #
    
    @classmethod
    async def write_file(
        cls,
        query: str
    )->dict:
        WRITE_FILE_ROUTE_PROMPT: str = """
        你是写作助手。
        根据用户的输入，进行相应的写作，写作的内容200字以内，写作的内容保存在content字段。
        返回json，固定格式如下:
        {
            "content":""
        }

        不要解释。
        只输出JSON。
        """
                
        #llm: ChatTongyi=await cls._get_llm_graph_model()
        
        llm: ChatOpenAI=QWen3BModel().llm_local_qwen3B()
        
        result: AIMessage = await llm.ainvoke([("system",WRITE_FILE_ROUTE_PROMPT),("human",query)])
        
        usage: UsageMetadata | None = result.usage_metadata
        
        assert usage is not None
        WorkFlowToolRouter.input_token+=usage.get("input_tokens",0)
        WorkFlowToolRouter.output_token+=usage.get("output_tokens",0)
        WorkFlowToolRouter.total_token+=usage.get("total_tokens",0)
        
        content: str = result.content.strip() # type: ignore
        json_match: re.Match[str] | None = re.search(r"\{[\s\S]*?\}", content)
        if not json_match:
            return {"content":""}
        try:
            json_data = json.loads(json_match.group())
            return json_data
        except Exception:
            return {"content":""}