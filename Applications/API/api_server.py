from fastapi import FastAPI
import sys
from pathlib import Path

from Capability.MCP.mcp_models import MCPTool
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from starlette.middleware.sessions import (
    SessionMiddleware
)

from  Applications.API.routers.auth import (
    router as auth_router
)
from Applications.API.routers.chat import (
    router as chat_router
)
from Applications.Web.web_server import (
    router as web_router
)
from Applications.API.routers.conversation import (
    router as conversation_router
)




from contextlib import asynccontextmanager
from Core.Agent.agent_factory import AgentFactory
from Infrastructure.Storage.database import Base, engine
from Infrastructure.Storage import models
from Infrastructure.Configs.Configuration import Configuration
from langgraph.graph.state import CompiledStateGraph
from langchain_community.chat_models import ChatTongyi
from Capability.MCP.mcp_tools_init import mcp_tools_init






"""初始化数据库"""
Base.metadata.create_all(bind=engine)


"""初始化普通的Agent"""
agent_factory:AgentFactory = AgentFactory(config=Configuration(),prompt=AgentFactory._set_prompt_())


"""初始化现有的MCP Tool"""
mcp_tools_init()


"""FastAPI生命周期"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    agent:CompiledStateGraph=await agent_factory._get_agent()
    llm:ChatTongyi =await agent_factory._get_ChatTongyi_model()
    app.state.agent = agent
    app.state.llm   = llm 
    yield
    pass


"""create FastAPI app"""
app: FastAPI = FastAPI(
    title="EveryoneAgent",
    lifespan=lifespan
)


"""add middleware"""
app.add_middleware(

    SessionMiddleware,
    secret_key="test_key_1234"
)


app.include_router(
    auth_router
)

app.include_router(
    web_router
)

app.include_router(
    chat_router
)

app.include_router(
    conversation_router
)


@app.get("/")
async def root() -> dict:

    return {
        "message": "EveryoneAgent"
    }