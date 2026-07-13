from dataclasses import dataclass

from pydantic import BaseModel


"""MCP模型"""

class MCPTool(BaseModel):

    tool_name: str
    
    server_name: str
    
    server_path: str

    description: str
    
    transport: str="stdio"
    
    server_url: str=""
    



"""MCP结果"""

class MCPResult(BaseModel):

    success: bool

    content: str

    metadata: dict = {}