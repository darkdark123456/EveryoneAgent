from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from Knowledge.RAGPipeline.retriever import (
    RetrieverManager
)
from Knowledge.RAGPipeline.context_builder import (
    ContextBuilder
)

from langchain_core.documents import Document

docs: list[Document] = RetrieverManager.retrieve(
    "什么是Prompt Engineering"
)
    
context:str = ContextBuilder.build(
    docs
)

print(context)