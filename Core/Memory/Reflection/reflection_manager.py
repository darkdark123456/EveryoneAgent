from sqlalchemy.orm import Session
from Core.Memory.Reflection.reflection_service import ReflectionService
from Core.Memory.Reflection.reflection_schema import ReflectionResult
from Infrastructure.Storage.crud import (
    get_graph_memories, 
    get_message_count, 
    get_recent_messages, 
    get_reflection_state, 
    get_summary, 
    reflection_exists,
    update_reflection_state)
from Infrastructure.Storage.models import ConversationSummary, MemoryGraph, Message, ReflectionState


class ReflectionManager:

    REFLECTION_TRIGGER = 3 #测试用例
    @classmethod
    async def check_and_update_reflection(
        cls,
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> None:
        
        total_count: int = get_message_count(
        db,
        conversation_id
    )
        state:ReflectionState | None = get_reflection_state(
        db,
        conversation_id
    )
        
        last_count: int = (
            state.last_reflection_count
            if state
            else 0
    )
                
        delta: int = (
            total_count
            -
            last_count
        )
        
        
        if (
            delta
            <
            cls.REFLECTION_TRIGGER
        ):
            return
        
        
        summary: ConversationSummary | None = get_summary(
            db,
            conversation_id
            )
        
        summary_text: str = (
            summary.summary
            if summary
            else ""
        ) # type: ignore
        
        
        
        graph_memories: list[MemoryGraph] | None = (
            get_graph_memories(
                db,
                user_id
            )
        )
        
        graph_text: str = (
            "\n".join(
                [
                    f"{memory.source} {memory.relation} {memory.target}"
                    for memory in graph_memories
                ]
            )
            if graph_memories
            else ""
        )
        
        
        messages: list[Message] = (
            get_recent_messages(
                db,
                conversation_id,
                6
            )
        )
        
        message_text: str = "\n".join(
            [
                f"{msg.role}: {msg.content}"
                for msg in messages
            ]
        )
        
        reflection_result: ReflectionResult = (
            await ReflectionService.generate_reflection(
                summary_text,
                graph_text,
                message_text
            )
        )
        
        update_count: int =0
        
        for reflection in reflection_result.reflections:
            
            if not reflection_exists(
                db,
                conversation_id,
                reflection.reflection_type,
                reflection.content
            ):
            
                await ReflectionService.save_reflections(
                    db,
                    conversation_id,
                    reflection
                )
                
                update_count += 1
                
        await update_reflection_state(
            db,
            conversation_id,
            last_count + update_count
        )