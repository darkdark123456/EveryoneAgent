from enum import Enum
from pydantic import BaseModel

class ReflectionType(str, Enum):

    LONG_TERM_GOAL = "long_term_goal"

    SHORT_TERM_GOAL = "short_term_goal"

    PROJECT = "project"

    INTEREST = "interest"

    NEXT_STEP = "next_step"

    INSIGHT = "insight"


class ReflectionItem(BaseModel):

    reflection_type: str

    content: str

    confidence: float

    importance: int


class ReflectionResult(BaseModel):

    reflections: list[ReflectionItem]