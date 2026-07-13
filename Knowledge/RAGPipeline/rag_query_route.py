RAG_KEYWORDS: list = [

    "提示工程",
    "RAG",
    "知识图谱",
    "Prompt",
    "知识库",
    "文档",
    "根据资料",
    "根据PDF",
    "LangChain",
    "LangGraph"
]


class QueryRouter:
    @staticmethod
    def need_rag(query: str) -> bool:
        for keyword in RAG_KEYWORDS:
            if keyword in query:
                return True
        return False