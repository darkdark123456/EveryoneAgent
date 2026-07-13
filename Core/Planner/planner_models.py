from pydantic import BaseModel


class PlanStep(BaseModel):

    step_id: int

    tool_name: str

    arguments: dict


class PlannerResult(BaseModel):

    goal: str
    steps: list[PlanStep]
