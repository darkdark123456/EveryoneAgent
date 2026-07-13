from Infrastructure.Storage.models import ConversationSummary, MemoryGraph, ReflectionMemory, UserMemory
from Core.Memory.KV.memory_ranker import MemoryRanker

class MemoryScore:
    @staticmethod
    def score_kv(
        memory: UserMemory
    ) -> float:
        return MemoryRanker.score(memory)
    
    @staticmethod
    def score_reflection(
        reflection: ReflectionMemory
    ) -> float:
        return (

        reflection.importance

        *
        reflection.confidence

        *
        1.5
    )
    @staticmethod
    def score_graph(
        graph_memory: MemoryGraph
    ) -> float:
        GRAPH_WEIGHT: dict[str, int] = {

        "开发":10,

        "工作于":10,

        "研究":8,

        "喜欢":6,

        "提到":3
    }
        
        return (
        GRAPH_WEIGHT.get(
            graph_memory.relation,
            1
        )
    )
    @staticmethod
    def score_summary(
        summary_memory: ConversationSummary
    ) -> float:
        return 8