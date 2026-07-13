from langchain_chroma import Chroma

from Knowledge.RAGPipeline.embedder import (
    EmbeddingFactory
)

from langchain_openai import OpenAIEmbeddings
class VectorStoreManager:
    """
    Chroma管理器
    """

    @staticmethod
    def get_store() -> Chroma:

        embeddings: OpenAIEmbeddings= (
            EmbeddingFactory._get_embedding()
        )

        store: Chroma = Chroma(

            collection_name="everyone_agent",

            embedding_function=embeddings,
        

            persist_directory=
            "Knowledge/VectorStore/chroma_db"
        )

        return store