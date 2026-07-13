"""
上下文构造器
"""

from langchain_core.documents import (
    Document
)


class ContextBuilder:

    @staticmethod
    def build(
        docs: list[Document]
    ) -> str:

        context: str = ""

        for i, doc in enumerate(docs):

            context += (
                f"\n\n【知识{i+1}】\n"
            )

            context += (
                doc.page_content
            )

        return context