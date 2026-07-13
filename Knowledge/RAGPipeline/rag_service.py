from Knowledge.RAGPipeline.rag_chain import (
    RAGPipeline
)



class RAGService:

    @staticmethod
    def build_context(
        question: str
    ) -> str:

        context = (
            RAGPipeline.retrieve_context(
                question
            )
        )

        return f"""
知识库内容：

{context}

用户问题：

{question}
"""