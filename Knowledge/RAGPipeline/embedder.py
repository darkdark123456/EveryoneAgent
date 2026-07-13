from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv,find_dotenv
import os

class EmbeddingFactory:
    
    """
    Embedding工厂
    """
    open_api_key: str | None = None
    google_api_key: str | None = None
    
    @staticmethod
    def _get_openai_api_key() -> str:
        load_dotenv(find_dotenv())
        EmbeddingFactory.open_api_key = os.getenv("OPENAI_API_KEY")
        if not EmbeddingFactory.open_api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env file")
        return EmbeddingFactory.open_api_key
    @staticmethod
    def _get_google_api_key() -> str:
        load_dotenv(find_dotenv())
        EmbeddingFactory.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not EmbeddingFactory.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in .env file")
        return EmbeddingFactory.google_api_key
    @staticmethod
    def _get_embedding() -> OpenAIEmbeddings:

        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(model="embedding-2", 
                                                        api_key=EmbeddingFactory._get_openai_api_key(),  # type: ignore
                                                        base_url="https://open.bigmodel.cn/api/paas/v4/") # type: ignore
        
        return embeddings