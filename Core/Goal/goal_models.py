from enum import Enum

from pydantic import BaseModel


class GoalItem(BaseModel):

    goal_type: str

    title: str

    description: str

    confidence: float

    importance: int
    
class GoalResult(BaseModel):

    goal_type: str

    title: str

    description: str

    confidence: float

    importance: int
    
class GoalStatus(str, Enum):

    ACTIVE = "active"

    COMPLETED = "completed"

    ABANDONED = "abandoned"