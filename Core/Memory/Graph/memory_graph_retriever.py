from sqlalchemy.orm import Session
from sqlalchemy import or_
from Infrastructure.Storage.models import MemoryGraph


class GraphRetriever:
    @staticmethod
    def get_entity_relations(

        db: Session,

        user_id: int,

        entity_name: str,

    )->  list[MemoryGraph]:
        
    
        return (

        db.query(MemoryGraph)
        .filter(

            MemoryGraph.user_id
            ==
            user_id,

            or_(
                MemoryGraph.source == entity_name,
                MemoryGraph.target == entity_name
            )
        )

        .all()
)