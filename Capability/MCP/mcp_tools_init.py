from Capability.MCP.mcp_registry import MCPRegistry
from Capability.MCP.mcp_models import MCPTool
from Infrastructure.Utils.Logger import SingletonLogger

def mcp_tools_init() -> None:
    
        SingletonLogger().info(f"mcp tools init...")
        SingletonLogger().info(f"==="*50+'\n\n')
        SingletonLogger().info(f"query weather mcp tools register...")
        MCPRegistry.register(

            MCPTool(
                tool_name="query_weather",

                server_name="WeatherServer",

                server_path="C:/Users/mzc228699/Documents/AIAgentProject/EveryoneAgent/Capability/Tools/weather_server.py",

                description="天气查询,本地Python stdio MCP 服务"
            )
      )
         
        SingletonLogger().info(f"query weather mcp tools ready...\n\n")
        SingletonLogger().info(f"write file mcp tools register...")
        MCPRegistry.register(

            MCPTool(
                tool_name="write_file",

                server_name="WriteServer",

                server_path="C:/Users/mzc228699/Documents/AIAgentProject/EveryoneAgent/Capability/Tools/write_server.py",
                description="文件写入,本地Python stdio MCP 服务"
            )
        )
        SingletonLogger().info(f"write file mcp tools ready...\n\n")
        SingletonLogger().info(f"高德地图 mcp tools register...")
        MCPRegistry.register(

            MCPTool(
                tool_name="maps_",
                server_name="map_server",
                server_url="https://mcp.api-inference.modelscope.net/89ef2b5c35b544/mcp",
                transport="streamable_http",
                server_path="",
                description="高德地图MCP远程服务，支持地址解析，坐标查询，地点搜索，路径规划等"
            )
        )
        
        SingletonLogger().info(f"高德地图 mcp tools ready...\n\n")
        SingletonLogger().info("all mcp tools register success...")
        SingletonLogger().info(f"==="*50)