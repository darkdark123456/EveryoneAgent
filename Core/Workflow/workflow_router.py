"""
问题路由器
"""
from pathlib import Path
import sys
import json
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from Core.Workflow.workflow_router_type import WorkFlowRouteType
from Core.Workflow.workflow_key_set import (MEMORY_KEYWORDS, 
                                            TOOL_KEYWORDS,
                                            RAG_KEYWORDS)


class WorkFlowQueryRouter:
    rules: dict={}
    def __init__(self) -> None:
        pass
    @classmethod
    def route(
        cls,
        query: str
    ) -> WorkFlowRouteType:
        query = query.lower()
        for keyword in MEMORY_KEYWORDS:

            if keyword in query:

                return WorkFlowRouteType.MEMORY

        for keyword in TOOL_KEYWORDS:

            if keyword in query:

                return WorkFlowRouteType.TOOL

        for keyword in RAG_KEYWORDS:

            if keyword in query:

                return WorkFlowRouteType.RAG
        return WorkFlowRouteType.CHAT
    @classmethod
    def _load_rules(cls) -> None:
        if cls.rules.__len__()>0:
            return
        rulers_path: Path=Path(__file__).parent / "WorkFlowRouterConfig"/"workflow_router_rulers.json"
        with rulers_path.open("r",encoding="utf-8") as f:
            cls.rules = json.load(f)
    @classmethod
    def route_from_json(cls,query: str)->WorkFlowRouteType:
        cls._load_rules()
        query = query.lower()

        for keyword in cls.rules["memory"]:

            if keyword in query:

                return WorkFlowRouteType.MEMORY

        for keyword in cls.rules["tools"]:

            if keyword in query:

                return WorkFlowRouteType.TOOL

        for keyword in cls.rules["rag"]:

            if keyword in query:

                return WorkFlowRouteType.RAG
        
        for keyword in cls.rules["chat"]:

            if keyword in query:

                return WorkFlowRouteType.CHAT
        
        return WorkFlowRouteType.UNKNOWN