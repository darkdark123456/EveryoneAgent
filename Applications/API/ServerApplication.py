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




class ServerIntelligenceAgent:
    def __init__(self,config: Configuration,prompt: str):
        self.mcp_client: MultiServerMCPClient
        self.agent: CompiledStateGraph
        self.model: ChatTongyi
        self.prompt= prompt
        self.config = config
        
        if(self._check_prompt()==False):
            raise ValueError("cannot find prompt")
        
        if(self._check_config()==False):
            raise ValueError("cannot find config")
        
        self._init_mcp_client()
        
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
        return self.config
    
    def _init_mcp_client(self) -> None:
        self.mcp_client = MultiServerMCPClient(Configuration.load_servers())
    
    @asynccontextmanager
    async def _life_span(self,app: FastAPI):
        SingletonLogger().info(f"mcp agent starting...")
        os.environ["DASHSCOPE_API_KEY"] = self.config.api_key
   
        try:
            tools: List[BaseTool] = await self.mcp_client.get_tools()
            SingletonLogger().info(f"Loaded {len(tools)}Mcp Tools： {[t.name for t in tools]}")
        except Exception as e:
            SingletonLogger().error(f"mcp connect failed: {e}")
            tools: List[BaseTool] = []
        self.model = ChatTongyi(model=self._get_config().model,api_key=self._get_config().api_key) # type: ignore

        self.agent= create_agent(model=self.model,tools=tools,
                                                  system_prompt=self._get_prompt(),
                                                  checkpointer=MemorySaver().get_memorysaver())
        
        app.state.agent = self.agent
        yield
    
    async def ainvoke(self,message:dict,config:RunnableConfig) -> dict[str,Any]:
        return await self.agent.ainvoke(message,config=config)


class FastApiServerAgent:
    class ChatRequest(BaseModel):
        message: str
        thread_id: str = "1"
        
    class ChatResponse(BaseModel):
        content: str
        status: str = "success"
        error: str = "error"
        
    @asynccontextmanager
    async def _lifespan_wrapper_(self,app: FastAPI):
        async with self.agent._life_span(app):
            yield

    
    def __init__(self,server_intelligence_agent:ServerIntelligenceAgent) -> None:
        self.agent = server_intelligence_agent
        self.application: FastAPI= FastAPI(lifespan=self._lifespan_wrapper_)
        
        
        # 允许跨域（方便前端调试）
        self.application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        
        @self.application.exception_handler(RequestValidationError)
        async def val_err_handler(request, exc):
            print("error: ", exc.errors())
            print("body: ", exc.body)
            return JSONResponse(
                status_code=422,
                content={"detail": exc.errors(), "body": exc.body}
            )     
            
        @self.application.post("/chat", response_model=FastApiServerAgent.ChatResponse)
        async def chat_endpoint(request: FastApiServerAgent.ChatRequest):
            if not self.agent:
                raise HTTPException(status_code=500, detail="Agent not initialized")

            run_config:RunnableConfig = {"configurable": {"thread_id": request.thread_id}}
            
            try:
                SingletonLogger().info(f"received message: {request.message}")
                result = await self.agent.ainvoke({"messages": [HumanMessage(content=request.message)]},run_config)
                if "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    return FastApiServerAgent.ChatResponse(content=last_message.content)
                else:
                    return FastApiServerAgent.ChatResponse(content="response is empty", status="empty")
            except Exception as e:
                SingletonLogger().error(f"handler error: {traceback.format_exc()}")
                return FastApiServerAgent.ChatResponse(content="", status="error", error=str(e))   
 
    def run(self):
        uvicorn.run(self.application, host="0.0.0.0", port=8000)



# if __name__ == "__main__":
#     server_intelligence_agent = ServerIntelligenceAgent(config=Configuration(),prompt=ServerIntelligenceAgent._set_prompt_())
#     fast_api_server = FastApiServerAgent(server_intelligence_agent)
#     fast_api_server.run()
    
