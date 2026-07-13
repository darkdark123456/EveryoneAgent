from langchain_core.documents import (
    Document
)

from Knowledge.VectorStore.vector_store import (
    VectorStoreManager
)

from langchain_chroma import Chroma
class RetrieverManager:
    """
    检索器
    """

    @staticmethod
    def retrieve(
        query: str
    ) -> list[Document]:

        store: Chroma= (
            VectorStoreManager.get_store()
        )

        results: list[Document] = store.similarity_search(
            query=query,
            k=3
        )

        return results