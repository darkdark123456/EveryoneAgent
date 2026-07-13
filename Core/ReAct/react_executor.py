from mcp.types import CallToolResult

from Capability.MCP.mcp_client import (
    MCPClient
)

from Core.ReAct.react_models import (
    ToolAction
)


class ReActExecutor:

    @classmethod
    async def execute(
        cls,
        action: ToolAction
    ) -> CallToolResult:

        return await MCPClient.call_tool(

            tool_name=action.tool_name,

            **action.arguments
        )