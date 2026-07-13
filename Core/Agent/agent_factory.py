"""
Agent工厂
"""
import os
import sys
import json
import logging
from   typing import Dict, Any
from   contextlib import asynccontextmanager
import traceback
import uvicorn
from   pydantic import BaseModel
from   pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from Infrastructure.Configs.Configuration import Configuration,config
from Infrastructure.Utils.Logger import SingletonLogger
from typing import List
from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from Core.Memory.KV.memory_saver import MemorySaver
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware




class AgentFactory:
    def __init__(self,config: Configuration,prompt: str):
        self.mcp_client: MultiServerMCPClient
        self.agent: CompiledStateGraph
        self.model: ChatTongyi
        self.prompt= prompt
        self.config = config
        self.tools:list[BaseTool]=[]
        self.agent_id: int=0
        
        if(self._check_prompt()==False):
            raise ValueError("cannot find prompt")
        
        if(self._check_config()==False):
            raise ValueError("cannot find config")
        
        
        
    def _check_prompt(self) -> bool:
        if self.prompt== "":
            with open("Capability/Prompts/agent_prompts.txt", "r", encoding="utf-8") as f:
                self.prompt= f.read()        
        return True if self.prompt else False

    @staticmethod
    def _set_prompt_() -> str:
        with open("Capability/Prompts/agent_prompts.txt", "r", encoding="utf-8") as file:
            prompt: str = file.read()
        if prompt == "":
            prompt = "你是一个智能助手，可以连接多种外部工具来帮助用户解决问题。"
        return prompt
    def _get_prompt(self) -> str:
        return self.prompt
    
    def _check_config(self) -> bool:
        if not self.config.load_servers():
            return False
        return True
    
    def _get_config(self) -> Configuration:
        if not self._check_config():
            raise ValueError("cannot find config")
        return self.config
    
    def _init_mcp_client(self) -> None:
        self.mcp_client = MultiServerMCPClient(Configuration.load_servers())

    def _init_weather_client(self) -> None:
        self.mcp_client = MultiServerMCPClient(Configuration.load_servers("weather_config.json"))
    
    def _init_docunment_client(self) -> None:
        self.mcp_client = MultiServerMCPClient(Configuration.load_servers("document_config.json"))
    
    def _init_map_client(self) -> None:
        self.mcp_client = MultiServerMCPClient(Configuration.load_servers("map_config.json"))
    
    def add_tool_for_agent(self,tool:BaseTool):
        self.tools.append(tool)
    
    async def _get_ChatTongyi_model(self) -> ChatTongyi:
        os.environ["DASHSCOPE_API_KEY"] = self.config.api_key
        
        if not self._get_config().model:
            raise ValueError("model is None")
        
        if not self._get_config().api_key:
            raise ValueError("api_key is None")
        
        model: ChatTongyi=ChatTongyi(model=self._get_config().model,api_key=self._get_config().api_key) # type: ignore
        return model
    
    """普通的agent 无需mcp"""
    async def _get_agent(self) -> CompiledStateGraph:
        self.agent_id=0
        try:
            #self._init_mcp_client()
            #self.tools= await self.mcp_client.get_tools()
            self.tools: List[BaseTool] = []
            #SingletonLogger().info(f"Loaded {len(self.tools)} Mcp Tools： {[t.name for t in self.tools]}")
        except Exception as e:
            SingletonLogger().error(f"mcp connect failed: {e}")
            tools: List[BaseTool] = []
        self.model =  await self._get_ChatTongyi_model()
        self.agent = create_agent(model=self.model,
                                  tools=self.tools,
                                  system_prompt=self._get_prompt(),
                                  checkpointer=MemorySaver().get_memorysaver())
        return self.agent
    
    async def get_weather_agent(self) -> CompiledStateGraph:
        self.agent_id=1
        self._init_weather_client()
        self.tools=await self.mcp_client.get_tools()
        SingletonLogger().info(f"Weather Agent Loaded {len(self.tools)} Mcp Tools： {[t.name for t in self.tools]}")

        self.model =  await self._get_ChatTongyi_model()
        self.agent = create_agent(model=self.model,
                                  tools=self.tools,
                                  system_prompt=self._get_prompt(),
                                  checkpointer=MemorySaver().get_memorysaver())
        return self.agent
    async def get_document_agent(self) -> CompiledStateGraph:
        self.agent_id=2
        self._init_docunment_client()
        self.tools=await self.mcp_client.get_tools()
        SingletonLogger().info(f"Document Agent Loaded {len(self.tools)} Mcp Tools： {[t.name for t in self.tools]}")

        self.model =  await self._get_ChatTongyi_model()
        self.agent = create_agent(model=self.model,
                                  tools=self.tools,
                                  system_prompt=self._get_prompt(),
                                  checkpointer=MemorySaver().get_memorysaver())
        return self.agent
    
    async def get_map_agent(self) -> CompiledStateGraph:
        self.agent_id=3
        self._init_map_client()
        self.tools=await self.mcp_client.get_tools()
        SingletonLogger().info(f"Map Agent Loaded {len(self.tools)} Mcp Tools： {[t.name for t in self.tools]}")

        self.model =  await self._get_ChatTongyi_model()
        self.agent = create_agent(model=self.model,
                                  tools=self.tools,
                                  system_prompt=self._get_prompt(),
                                  checkpointer=MemorySaver().get_memorysaver())
        return self.agent
    async def get_custom_agent(self) -> None:
        pass