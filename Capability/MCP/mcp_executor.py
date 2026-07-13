from Capability.MCP.mcp_client import MCPClient
from mcp.types import ListToolsResult
from mcp.types import CallToolResult

class MCPExecutor:

    @classmethod
    async def execute(
        cls,
        tool_name:str,
        **kwargs
    ) -> CallToolResult:
        return await MCPClient.call_tool(
            tool_name,
            **kwargs
        )