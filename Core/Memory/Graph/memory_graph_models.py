from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class GraphEntity:

    name: str
    
    entity_type: str
    
    
@dataclass
class GraphRelation:

    source: str

    relation: str

    target: str
    
    importance: int
    
    
class GraphExtractionResult(
    BaseModel
):

    source: str

    relation: str

    target: str

    importance: int
    


class GraphRelationList(BaseModel):

    relations: list[GraphExtractionResult]