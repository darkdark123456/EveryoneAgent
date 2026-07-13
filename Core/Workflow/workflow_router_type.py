from enum import Enum


class WorkFlowRouteType(str, Enum):
    CHAT = "chat"
    RAG = "rag"
    MEMORY = "memory"
    TOOL = "tool"
    UNKNOWN = "unknown"
    
    
