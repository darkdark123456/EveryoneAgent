import asyncio
import json
import os
import sys
from pathlib import Path
from   typing import Any, Dict, List

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langchain.agents import create_agent
from Infrastructure.Utils.Logger import SingletonLogger
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from Infrastructure.Configs.Configuration import Configuration,config
from Core.Memory.KV.memory_saver import  MemorySaver



class ClientIntelligenceAgent:
    def __init__(self) -> None:
        pass
    @staticmethod
    def _get_prompt_() -> str:
        with open("Capability/Prompts/agent_prompts.txt", "r", encoding="utf-8") as file:
            prompt: str = file.read()
        if prompt == "":
            prompt = "你是一个智能助手，可以连接多种外部工具来帮助用户解决问题。"
        return prompt
    @staticmethod
    async def _run_chat_loop_() -> None:
        
        cfg:Configuration = Configuration()
        os.environ["DASHSCOPE_API_KEY"] = cfg.api_key
        
        servers_cfg: Dict[str, Any] = Configuration.load_servers()

        mcp_client: MultiServerMCPClient = MultiServerMCPClient(servers_cfg)

        tools: List[BaseTool] = await mcp_client.get_tools() 
        SingletonLogger().info(f"Loaded {len(tools)}Mcp Tools： {[t.name for t in tools]}")
        model: ChatTongyi = ChatTongyi(model=cfg.model,api_key=cfg.api_key) # type: ignore

        agent: CompiledStateGraph  = create_agent(model=model,tools=tools,
                                                  system_prompt=ClientIntelligenceAgent._get_prompt_(),
                                                  checkpointer=MemorySaver().get_memorysaver())
        SingletonLogger().info(f"Loaded Agent...")
        SingletonLogger().info(f"mcp agent started")
        while True:
            user_input: str = input("\n You: ").strip()
            if user_input.lower() == "quit":
                break
            try:
                result: Dict[str,Any] = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config
            )
                last_message: AIMessage = result['messages'][-1]
                SingletonLogger().info(f"AI: {last_message.content}")
            except Exception as exc:
                SingletonLogger().error(f"error：{exc}")
                
        SingletonLogger().info(f"mcp agent stopped")
    @staticmethod
    def _run_():
        asyncio.run(ClientIntelligenceAgent._run_chat_loop_())


if __name__ == "__main__":
    ClientIntelligenceAgent._run_()
