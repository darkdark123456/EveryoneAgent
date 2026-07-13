from typing import Tuple

from langchain_openai import ChatOpenAI

from Core.Agent.agent_factory import AgentFactory
from Core.Memory.Graph.memory_graph_models import GraphEntity,GraphRelation,GraphRelationList
from langchain_community.chat_models import ChatTongyi
from Infrastructure.Configs.Configuration import Configuration
from langchain_core.runnables import Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from Core.Models.qwen3B_model import QWen3BModel
import json

from Infrastructure.Utils.Logger import SingletonLogger

GRAPH_PROMPT: str = """
你是知识图谱关系抽取器。

任务：

从用户输入中提取：

source
relation
target
importance

要求：

1 返回JSON

2 不要解释

3 importance范围1-10

4 可以返回多个关系

5 尽量简洁

6 如果source和target没有明显关系，它们之间的relation设置为提及，importance设置为5

例子：

输入：

我正在开发EveryoneAgent

输出：

{
 "relations":[
   {
      "source":"用户",
      "relation":"开发",
      "target":"EveryoneAgent",
      "importance":9
   }
 ]
}

"""


class GraphExtractor:
    input_token:int=0
    output_token:int=0
    total_token:int=0
    def __init__(self) -> None:
        pass
    @staticmethod
    async def get_token_used()->Tuple[int,int,int]:
        return GraphExtractor.input_token,GraphExtractor.output_token,GraphExtractor.total_token
    
    @staticmethod
    async def _extract(text: str) -> GraphRelationList:
        llm_online: ChatTongyi =await GraphExtractor._get_llm_graph_model()

        llm: ChatOpenAI =await GraphExtractor.get_local_qwen3b_model()
        message: list =[("system",GRAPH_PROMPT),("human",text)]
        
        result: AIMessage = await llm.ainvoke(message)   
        
        #import os
        #os.environ["SSL_CERT_FILE"] = r"E:\programme\miniconda3\ssl\cacert.pem" 
        usage = result.usage_metadata
        
        assert usage is not None
        GraphExtractor.input_token=usage.get("input_tokens",0)
        GraphExtractor.output_token=usage.get("output_tokens",0)
        GraphExtractor.total_token=usage.get("total_tokens",0)
        
        raw=result.content.strip() # type: ignore
        try:
            json_data = json.loads(raw)
            return GraphRelationList(**json_data)
        except Exception:
            return GraphRelationList(relations=[])
    @staticmethod
    async def _get_llm_graph_model() -> ChatTongyi:
        return await  AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()  # type: ignore
    @staticmethod
    async def get_local_qwen3b_model() -> ChatOpenAI:
        qwen3b_llm: ChatOpenAI=QWen3BModel().llm_local_qwen3B()
        return qwen3b_llm
        