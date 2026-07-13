from Knowledge.RAGPipeline.retriever import (
    RetrieverManager as Retriever
)

from langchain_core.documents import Document

class RAGPipeline:
    """
    RAG流程
    """

    @staticmethod
    def retrieve_context(
        question: str
    ) -> str:
        docs: list[Document] = Retriever.retrieve(question)
        context: str = "\n".join( doc.page_content for doc in docs)
        return context