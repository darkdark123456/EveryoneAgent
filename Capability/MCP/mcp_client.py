
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))
import asyncio

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult
from mcp.types import CallToolResult
from Capability.MCP.mcp_models import MCPTool
from Capability.MCP.mcp_registry import (
    MCPRegistry
)
from mcp.types import ListToolsResult
from mcp.types import CallToolResult
from mcp.client.streamable_http import streamable_http_client
class MCPClient:
    tools_list: ListToolsResult
    @classmethod
    async def call_tool(
        cls,
        tool_name: str,
        **kwargs
    ) -> CallToolResult:

        tool: MCPTool | None = MCPRegistry.get_tool(
            tool_name
        )

        if tool is None:

            raise ValueError(
                f"工具不存在:{tool_name}"
            )

        
        if tool.transport == "stdio":
            server: StdioServerParameters = StdioServerParameters(

                command="python",

                args=[
                    tool.server_path
                ]
            )

            async with stdio_client(
                server
            ) as (

                read_stream,
                write_stream

            ):
                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:

                    await session.initialize()
                    cls.tools_list = await session.list_tools()
                
                    result: CallToolResult = await session.call_tool(
                        name=tool_name,
                        arguments=kwargs
                    )

                    return result
        if tool.transport == "streamable_http":
            async with streamable_http_client(
                tool.server_url
            ) as (read_stream, write_stream,_):

                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:

                    await session.initialize()
                    cls.tools_list = await session.list_tools()
                
                    result: CallToolResult = await session.call_tool(
                        name=tool_name,
                        arguments=kwargs
                    )
                    return result
                
        return CallToolResult(content=[],structuredContent={},isError=False)
    @staticmethod      
    async def list_tools(
        server_name:str
        ):
        
        tool=MCPRegistry.get_tool(server_name)
        return tool