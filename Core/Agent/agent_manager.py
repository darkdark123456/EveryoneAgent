from Capability.MCP.mcp_client import MCPClient
from Capability.MCP.mcp_registry import MCPRegistry
from langgraph.graph.state import CompiledStateGraph
from langchain_core.tools import BaseTool
from Core.Agent.agent_factory import AgentFactory
from Core.Agent.agent_model import AgentType,Agent_ID
from Core.Planner.planner_executor import ToolResult
from Core.Planner.planner_models import PlannerResult
from Infrastructure.Configs.Configuration import Configuration
from mcp.types import CallToolResult

class AgentManager:
    def __init__(self):
        pass
    @staticmethod
    async def get_agent_list(agent_type_list: list[dict[str,str]]) -> list[CompiledStateGraph]:
        agent_list:list[CompiledStateGraph]=[]
        for agent_type in agent_type_list:
            if agent_type["agent_name"] == "weather_agent":
                agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="").get_weather_agent()
                agent_list.append(agent)
            elif agent_type["agent_name"] == "travel_agent":
       
                agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="").get_map_agent()
                agent_list.append(agent)
            elif agent_type["agent_name"] == "document_agent":
              
                agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="").get_document_agent()
                agent_list.append(agent)
            elif agent_type["agent_name"] == "general_agent":
                agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="")._get_agent()
                agent_list.append(agent)
            else:
                pass
        return agent_list
    @staticmethod
    async def agent_excutor_planner(
                                     result: list[dict[str,str]]
                                    ) -> str:
        if result is None:
            return ""
        
        answer_list: list[str]=[]
        
        write_argument: dict = {"content": ""}
        for data in result:
            agent_type: AgentType = AgentType(data["agent"])
            match agent_type:
                case AgentType.TRAVEL:
                   goal: str= data["goal"]
                   agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="").get_map_agent()
                   response: dict = await agent.ainvoke({"messages": goal},config={"configurable": {"thread_id": str(Agent_ID["map"])} })
                   answer:str=response["messages"][-1].content # type: ignore
                   write_argument["content"] += answer
                   answer_list.append(answer)
                   
                case AgentType.WEATHER:
                    goal: str= data["goal"]
                    agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="").get_weather_agent()
                    response: dict =await agent.ainvoke({"messages": goal},config={"configurable": {"thread_id": str(Agent_ID["weather"])} })
                    answer:str=response["messages"][-1].content # type: ignore
                    write_argument["content"] += answer
                    answer_list.append(answer)
                    
                case AgentType.GENERAL:
                    goal: str= data["goal"]
                    agent:CompiledStateGraph=await AgentFactory(config=Configuration(), prompt="")._get_agent()
                    response: dict =await  agent.ainvoke({"messages": goal},config={"configurable": {"thread_id": str(Agent_ID["general"])} })
                    answer:str=response["messages"][-1].content # type: ignore
                    write_argument["content"] += answer
                    answer_list.append(answer)    
                    
                case AgentType.DOCUMENT:
                    tool_result:CallToolResult = await MCPClient.call_tool(
                        tool_name="write_file",
                        **write_argument
                    )
                    
                case _:
                    pass
        
        answer: str=""
        for answer_ in answer_list:
            answer+=answer_
            answer+="\n"
        return answer