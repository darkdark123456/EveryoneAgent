from pathlib import Path
import sys
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from Knowledge.RAGPipeline.loader import (
    DocumentLoader
)

from langchain_core.documents import Document

from Knowledge.RAGPipeline.splitter import (
    TextChunkSplitter
)

from Knowledge.VectorStore.vector_store import (
    VectorStoreManager
)

from Infrastructure.Utils.Logger import SingletonLogger

from langchain_chroma import  Chroma
from langchain_core.documents import Document
from Knowledge.RAGPipeline.embedder import (
    EmbeddingFactory
)

from langchain_core.documents import Document
def ingest() -> None:
    """
    导入知识库
    """
    pdf_path: Path = root_path / "Knowledge" / "Documents" / "如何向 ChatGPT 提问以获得高质量答案：提示技巧工程完全指南.pdf"
    docs: list[Document] = DocumentLoader.load_pdf(

        file_path=str(pdf_path)
    )

    chunks = TextChunkSplitter.split(
        docs
    )
    
    store: Chroma = (
        VectorStoreManager.get_store()
    )
        
    BATCH_SIZE: int = 20

    for i in range(
        0,
        len(chunks),
        BATCH_SIZE
    ):

        batch = chunks[i:i+BATCH_SIZE]

        try:

            store.add_documents(batch)

            SingletonLogger().info(
                f"导入成功: {i + len(batch)}/{len(chunks)}"
            )

        except Exception as e:

            SingletonLogger().error(
                f"导入失败: {i}"
            )

    SingletonLogger().info("知识库导入完成")


if __name__ == "__main__":
    ingest()

    
    
    