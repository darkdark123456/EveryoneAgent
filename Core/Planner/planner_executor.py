import json
from typing import Any

from pydantic import BaseModel
from Capability.MCP.mcp_client import (
    MCPClient
)
from Core.Planner.planner_models import PlannerResult
from mcp.types import ListToolsResult
from mcp.types import CallToolResult
class ToolResult(BaseModel):

    step_id: int

    tool_name: str

    result: str
    
class PlannerExecutor:
    @staticmethod
    async def get_origin_coordinate():
        pass
    @classmethod
    async def execute_plan(
        cls,
        plan_list: list[PlannerResult]
    ) -> list[ToolResult]:
        
        results: list[ToolResult] = []
        write_arguments: dict = {"content":""}
        for plan in plan_list:
            for step in plan.steps:
                
                """如果使用query_weather工具，字段arguments里面必须包含city，且city必须是英文。"""
                if step.tool_name == "query_weather":
                    tool_result: CallToolResult = await MCPClient.call_tool(
                        tool_name=step.tool_name,
                        **step.arguments
                    )
                    
                    write_arguments["content"]  += tool_result.structuredContent["result"]+"\n\n" # type: ignore
                    
                    results.append(
                        ToolResult(
                            step_id=step.step_id,
                            tool_name=step.tool_name,
                            result=str(tool_result)
                        )
                    )
                    
                    
                if step.tool_name.startswith("maps_"):
                    
                    if step.tool_name == "maps_direction_driving":
                        if "origin" in step.arguments and "destination" in step.arguments:
                            start: CallToolResult= await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["origin"]
                           )
                            
                            end: CallToolResult = await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["destination"]
                           )
                           
                            if start  is None or end is None:
                                raise ValueError("无法获取当前地点或目标地点的经纬度")
                            print(start)
                            print(end)

                            start_json: Any = json.loads(start.content[0].text) # type: ignore
                            end_json: Any   = json.loads(end.content[0].text) # type: ignore
                            
                            start_coords = start_json["return"][0]["location"] # type: ignore
                            end_coords   = end_json["return"][0]["location"] # type: ignore

                            real_arguments: dict = {
                               "origin":start_coords,
                               "destination":end_coords
                           }
                    
                            tool_result: CallToolResult = await MCPClient.call_tool(
                                tool_name=step.tool_name,
                                **real_arguments
                            )
                            
                            results.append(
                            ToolResult(
                                step_id=step.step_id,
                                tool_name=step.tool_name,
                                result=str(tool_result)
                            )
                        )
                    
                            write_arguments["content"]  += str(tool_result)# type: ignore
                        else:
                            pass
                    elif step.tool_name == "maps_direction_walking":
                        if "origin" in step.arguments and "destination" in step.arguments:
                            start: CallToolResult= await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["origin"]
                           )
                            
                            end: CallToolResult = await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["destination"]
                           )
                           
                            if start  is None or end is None:
                                raise ValueError("无法获取当前地点或目标地点的经纬度")
                            print(start)
                            print(end)

                            start_json: Any = json.loads(start.content[0].text) # type: ignore
                            end_json: Any   = json.loads(end.content[0].text) # type: ignore
                            
                            start_coords = start_json["return"][0]["location"] # type: ignore
                            end_coords   = end_json["return"][0]["location"] # type: ignore

                            real_arguments: dict = {
                               "origin":start_coords,
                               "destination":end_coords
                           }
                    
                            tool_result: CallToolResult = await MCPClient.call_tool(
                                tool_name=step.tool_name,
                                **real_arguments
                            )
                            
                            results.append(
                            ToolResult(
                                step_id=step.step_id,
                                tool_name=step.tool_name,
                                result=str(tool_result)
                            )
                        )
                    
                            write_arguments["content"]  += str(tool_result)# type: ignore
                        
                    elif step.tool_name == "maps_geo":
                        tool_result: CallToolResult = await MCPClient.call_tool(
                            tool_name=step.tool_name,
                            **step.arguments["address"]
                        )
                        
                        results.append(
                            ToolResult(
                                step_id=step.step_id,
                                tool_name=step.tool_name,
                                result=str(tool_result)
                            )
                        )
                        
                    elif step.tool_name == "maps_bicycling":

                        if "origin" in step.arguments and "destination" in step.arguments:
                            start: CallToolResult= await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["origin"]
                           )
                            
                            end: CallToolResult = await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["destination"]
                           )
                           
                            if start  is None or end is None:
                                raise ValueError("无法获取当前地点或目标地点的经纬度")
                            print(start)
                            print(end)

                            start_json: Any = json.loads(start.content[0].text) # type: ignore
                            end_json: Any   = json.loads(end.content[0].text) # type: ignore
                            
                            start_coords = start_json["return"][0]["location"] # type: ignore
                            end_coords   = end_json["return"][0]["location"] # type: ignore

                            real_arguments: dict = {
                               "origin":start_coords,
                               "destination":end_coords
                           }
                    
                            tool_result: CallToolResult = await MCPClient.call_tool(
                                tool_name=step.tool_name,
                                **real_arguments
                            )
                            
                            results.append(
                            ToolResult(
                                step_id=step.step_id,
                                tool_name=step.tool_name,
                                result=str(tool_result)
                            )
                        )
                    
                            write_arguments["content"]  += str(tool_result)# type: ignore
                        
                    elif step.tool_name == "maps_direction_transit_integrated":
                        if "origin" in step.arguments and "destination" in step.arguments:
                            start: CallToolResult= await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["origin"]
                           )
                            
                            end: CallToolResult = await MCPClient.call_tool(
                                tool_name="maps_geo",
                                address=step.arguments["destination"]
                           )
                           
                            if start  is None or end is None:
                                raise ValueError("无法获取当前地点或目标地点的经纬度")
                            print(start)
                            print(end)

                            start_json: Any = json.loads(start.content[0].text) # type: ignore
                            end_json: Any   = json.loads(end.content[0].text) # type: ignore
                            
                            start_coords = start_json["return"][0]["location"] # type: ignore
                            end_coords   = end_json["return"][0]["location"] # type: ignore

                            real_arguments: dict = {
                               "origin":start_coords,
                               "destination":end_coords
                           }
                    
                            tool_result: CallToolResult = await MCPClient.call_tool(
                                tool_name=step.tool_name,
                                **real_arguments
                            )
                            
                            results.append(
                            ToolResult(
                                step_id=step.step_id,
                                tool_name=step.tool_name,
                                result=str(tool_result)
                            )
                        )
                            write_arguments["content"]  += str(tool_result)# type: ignore
                    else:
                        pass
                
                """如果使用write_file工具，字段arguments里面必须包含content。"""            
                if step.tool_name == "write_file":
                    tool_result: CallToolResult = await MCPClient.call_tool(
                        tool_name=step.tool_name,
                        **write_arguments
                    )
                    
                    results.append(
                        ToolResult(
                            step_id=step.step_id,
                            tool_name=step.tool_name,
                            result=str(tool_result)
                        )
                    )
        return results
    @classmethod
    async def collect_plan_results(
        cls,
        plan_tool_results: list[ToolResult]
    ) -> str:
        answer: str = ""
        for tool_result in plan_tool_results:
            answer += tool_result.result.structuredContent["result"]+"\n\n" # type: ignore
        return answer
    