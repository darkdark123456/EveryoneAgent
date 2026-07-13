from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader


class DocumentLoader:
    """
    文档加载器

    负责读取 Documents 目录中的文件
    """

    @staticmethod
    def load_txt(
        file_path: str
    ) -> list[Document]:
        """
        加载txt文件
        """

        loader: TextLoader = TextLoader(
            file_path=file_path,
            encoding="utf-8"
        )

        documents: list[Document] = loader.load()

        return documents
    @staticmethod
    def load_pdf(
        file_path: str
    ) -> list[Document]:
        """
        加载pdf文件
        """

        from langchain_community.document_loaders import PyPDFLoader

        loader: PyPDFLoader = PyPDFLoader(
            file_path=file_path
        )

        documents: list[Document] = loader.load()

        return documents