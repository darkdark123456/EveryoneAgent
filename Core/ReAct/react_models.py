from pydantic import BaseModel


class ToolAction(BaseModel):

    tool_name: str

    arguments: dict
    
    
    
class ReActStep(BaseModel):

    thought: str

    action: ToolAction | None
    
    
    


class ReActResult(BaseModel):

    thought: str

    action: ToolAction | None

    final_answer: str | None