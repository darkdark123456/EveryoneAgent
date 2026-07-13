import json

from sqlalchemy.orm import Session
from Core.Memory.Reflection.reflection_schema import ReflectionItem
from Infrastructure.Storage.models import ReflectionMemory
from Core.Agent.agent_factory import AgentFactory
from Core.Memory.Reflection.reflection_schema import ReflectionResult
from Core.Memory.Reflection.reflection_prompt_builder import REFLECTION_PROMPT
from Infrastructure.Configs.Configuration import Configuration
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage

from Infrastructure.Storage.models import ReflectionMemory
class ReflectionService:
    @classmethod
    async def generate_reflection(
        cls,
        summary_text: str,
        graph_text: str,
        message_text: str
    ) -> ReflectionResult:
        
        context: str = f"""
        【会话摘要】

        {summary_text}


        【知识图谱】

        {graph_text}


        【最近聊天记录】

        {message_text}
        """
        
        messages: list = [

            (
                "system",
                REFLECTION_PROMPT
            ),

            (
                "human",
                context
            )
        ]
        
        llm: ChatTongyi =await ReflectionService._get_llm_reflection_model()
        result: AIMessage = await llm.ainvoke(messages)    
        raw=result.content.strip() # type: ignore
        try:
            json_data = json.loads(raw)
            return ReflectionResult(**json_data)
        except Exception:
            return ReflectionResult(reflections=[])
        
    @staticmethod
    async def _get_llm_reflection_model() -> ChatTongyi:
        return await  AgentFactory(config=Configuration(), prompt="")._get_ChatTongyi_model()  
    
    @staticmethod
    async def save_reflections(
    db: Session,
    user_id: int,
    item: ReflectionItem
    ):
        reflection: ReflectionMemory = ReflectionMemory(

        user_id=user_id,

        reflection_type=
        item.reflection_type,

        content=
        item.content,

        confidence=
        item.confidence,

        importance=
        item.importance
    )
        
        db.add(reflection)

        db.commit()
    