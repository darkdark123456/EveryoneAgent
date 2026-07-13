from Core.Memory.MemoryOrchestrator.memory_models import RetrievedMemory


class MemoryContextBuilder:
    def __init__(self) -> None:
        pass
    @staticmethod
    def build(
        retrieved_memories: list[RetrievedMemory]
    ) -> str:
        
        lines: list[str] = []
        lines.append(
            "以下是用户相关记忆："
        )
        
        for memory in retrieved_memories:
            lines.append(

            f"[{memory.source}] "

            f"{memory.content}"
        )
            
        return "\n".join(lines)