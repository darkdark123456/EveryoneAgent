from pydantic import BaseModel
from enum import Enum


class AgentRouteResult(BaseModel):

    agent_name: str


class AgentType(str, Enum):

    TRAVEL = "travel_agent"

    WEATHER = "weather_agent"
    
    DOCUMENT = "document_agent"

    GENERAL = "general_agent"
    
    
Agent_ID: dict[str,int]={
    "weather":0,
    "document":1,
    "map":2,
    "general":3
}
