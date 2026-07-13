
from Core.Agent.agent_factory import AgentFactory
from Core.Memory.Summary.summary_service import SummaryService
from Infrastructure.Configs.Configuration import Configuration
from Infrastructure.Storage.crud import (
    get_message_count,
    get_summary,
    save_or_update_summary,
    get_messages_by_conversation
)

from Infrastructure.Storage.models import ConversationSummary, Message
from Infrastructure.Utils.Logger import SingletonLogger
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage


class SummaryManager:

    SUMMARY_TRIGGER:int = 4

    @classmethod
    def should_summarize(
        cls,
        total_count: int,
        summarized_count: int
    ) -> bool:
        return (
            total_count
            -
            summarized_count
            >=
            cls.SUMMARY_TRIGGER
        )
    @staticmethod
    async def _update_summary(
        old_summary: str,
        messages: list[Message]
    ) -> str:
        """
        增量更新摘要
        """

        if len(messages) == 0:

            return old_summary

        message_text = "\n".join(

            f"{msg.role}: {msg.content}"

            for msg in messages
        )

        prompt = f"""
        你是一个长期记忆压缩助手。
        已有摘要：
        {old_summary}
        新增对话：
        {message_text}
        请更新摘要。

        要求：

        1. 保留用户身份信息

        2. 保留用户偏好

        3. 保留项目进展

        4. 保留重要事实

        5. 删除重复内容

        6. 输出不超过300字

        直接输出新的摘要。
        """
        llm: ChatTongyi =await AgentFactory(config=Configuration(),prompt=prompt)._get_ChatTongyi_model()

        result: AIMessage = await llm.ainvoke(
            prompt
        )
        return result.content.strip() # type: ignore
    @classmethod
    async def check_and_update_summary(
        cls,
        db,
        conversation_id: int
    )-> None:

        total_count: int = (
            get_message_count(
                db,
                conversation_id
            )
        )

        summary: ConversationSummary | None  = (
            get_summary(
                db,
                conversation_id
            )
        )

        summarized_count:int = (
            summary.last_message_count
            if summary
            else 0
        ) # type: ignore

        if not cls.should_summarize(
            total_count,
            summarized_count # type: ignore
        ):
            return
        
        messages: list[Message] = get_messages_by_conversation(

        db=db,
        conversation_id=conversation_id
        )
        
        new_messages: list[Message] = messages[0:summarized_count]
        SingletonLogger().info(

        f"发现 {len(new_messages)} 条新消息需要摘要"
    )
        old_summary: str = ""
        if summary:

            old_summary = (
                summary.summary
                if summary
                else ""
            ) # type: ignore
            SingletonLogger().info(

            f"旧摘要：{old_summary}"
            )
        new_summary: str = await SummaryManager._update_summary(

            old_summary=old_summary,

            messages=new_messages
            )
        SingletonLogger().info(f"新摘要：{new_summary}")
        save_or_update_summary(
        db=db,
        conversation_id=conversation_id,
        summary=new_summary,
        last_message_count=summarized_count + SummaryManager.SUMMARY_TRIGGER# type: ignore
        )
        

        #当前总量-已经摘要的数量 剩下的数量是你要把messageg转换为摘要