from sqlalchemy.orm import Session
from Core.Memory.MemoryOrchestrator.memory_context_builder import MemoryContextBuilder
from Core.Memory.MemoryOrchestrator.memory_models import RetrievedMemory
from Core.Memory.MemoryOrchestrator.memory_score import MemoryScore
from Core.Memory.KV.memory_service import get_memories
from Infrastructure.Storage.crud import get_graph_memories, get_summary
from Infrastructure.Storage.models import ConversationSummary, MemoryGraph, ReflectionMemory, UserMemory
from Core.Memory.Reflection.reflection_retriever import ReflectionRetriever

class MemoryOrchestrator:
    TOP_K: int = 10
    @classmethod
    def retrieve_memories(
        cls,
        db: Session,
        user_id: int,
        conversation_id: int,
        query: str
    ) -> list[RetrievedMemory]:
        
        kv_memories: list[UserMemory] = (
            get_memories(
                db,
                user_id
            )
     )
        
        graph_memories: list[MemoryGraph]  | None = (
            get_graph_memories(
                db,
                user_id
            )
    )
        
        reflections: list[ReflectionMemory] = (
            ReflectionRetriever.get_top_reflections(
                db,
                user_id
            )
        )
        
        summary: ConversationSummary | None = (
            get_summary(
                db,
                conversation_id
            )
        )
        
        
        retrieved_results: list[
            RetrievedMemory
        ] = []
        
        
        for memory in kv_memories:
            retrieved_results.append(
            RetrievedMemory(

                source="kv",

                content=
                f"{memory.memory_key}={memory.memory_value}",

                score=
                MemoryScore.score_kv(
                    memory
                )
            )
        )
        
        
        for reflection in reflections:
            retrieved_results.append(

            RetrievedMemory(

                source="reflection",

                content=
                reflection.content,

                score=
                MemoryScore
                .score_reflection(
                    reflection
                )
            )
        )
        
        if graph_memories is not None:
            for graph in graph_memories:
                retrieved_results.append(

                RetrievedMemory(

                    source="graph",

                    content=
                    f"{graph.source}"
                    f"->{graph.relation}->"
                    f"{graph.target}",

                    score=
                    MemoryScore
                    .score_graph(
                        graph
                    )
                )
            )
        
        if summary is not None:
            retrieved_results.append(
                RetrievedMemory(
                    source="summary",
                    content=summary.summary, # type: ignore
                    score=MemoryScore.score_summary(summary)
                )
            )
            
        
        retrieved_results.sort(

            key=lambda x:x.score,

            reverse=True
        )    
                    
        return retrieved_results[:cls.TOP_K]
    
    @classmethod
    def build_prompt(
        cls,
        db: Session,
        user_id: int,
        conversation_id: int,
        query: str
    ) -> str:
        
        memories: list[RetrievedMemory] = (
        cls.retrieve_memories(
            db,
            user_id,
            conversation_id,
            query
        )
     )
        return (
            MemoryContextBuilder.build(
                memories
            )
    )