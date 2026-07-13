from Infrastructure.Storage.models import (
    MemoryGraph,
    
)

from Core.Memory.Graph.memory_graph_models import GraphEntity,GraphRelation,GraphExtractionResult,GraphRelationList
from sqlalchemy.orm import Session

class GraphService:
    def __init__(self) -> None:
        pass
    @staticmethod
    def save_relations(

        db: Session,

        user_id: int,

        graph_relations: list[GraphExtractionResult]
    ):
        if graph_relations is None:

            return
        
        for item in graph_relations:

            graph: MemoryGraph = MemoryGraph(

                user_id=user_id,

                source=item.source, 

                relation=item.relation, 

                target=item.target,

                importance=item.importance 
            )


            exists: MemoryGraph | None = (

                db.query(MemoryGraph)

                .filter(

                    MemoryGraph.user_id
                    ==
                    user_id,

                    MemoryGraph.source
                    ==
                    item.source, 

                    MemoryGraph.relation
                    ==
                    item.relation,

                    MemoryGraph.target
                    ==
                    item.target
                )

                .first()
            )
    
            if exists is not None:
                continue
            db.add(graph)
        db.commit()