from Capability.MCP.mcp_models import MCPTool
from langchain_core.tools import BaseTool
from typing import List
"""MCP Registry"""
class MCPRegistry:

    _tools: dict = {}

    @classmethod
    def register(
        cls,
        tool: MCPTool
    ) -> None:
        cls._tools[
            tool.tool_name
        ] = tool

    @classmethod
    def get_tool(
        cls,
        tool_name: str
    ):
        match = cls._tools.get(tool_name, None)
        
        if match is  not None:
            return match
        
        if tool_name.startswith("maps_"):
            return cls._tools.get("maps_", None)
        
        return None
    @classmethod
    def get_all_tools(cls,) -> dict:
        return cls._tools


