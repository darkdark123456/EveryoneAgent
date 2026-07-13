from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


class TextChunkSplitter:
    """
    文档切块器
    """

    @staticmethod
    def split(
        documents: list[Document]
    ) -> list[Document]:
        """
        文档切块
        """

        splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(

            chunk_size=500,

            chunk_overlap=100
        )

        chunks: list[Document] = splitter.split_documents(
            documents
        )

        return chunks