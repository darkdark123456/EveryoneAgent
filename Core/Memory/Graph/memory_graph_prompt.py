from Core.Memory.Graph.memory_graph_models import GraphExtractionResult
from Infrastructure.Storage.models import MemoryGraph


class GraphPromptBuilder:
    @staticmethod
    def build(
        relations: list[MemoryGraph]
    ) -> str:
        if not relations:
            return ""
        lines = []

        for releation in relations:

            lines.append(

                f"{releation.source}"

                f" {releation.relation} "

                f"{releation.target}"
            )
            
        return (

            "知识图谱信息：\n"

            +

            "\n".join(lines)
        )
        