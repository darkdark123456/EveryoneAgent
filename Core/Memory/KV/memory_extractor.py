import json
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re

from Core.Models.qwen3B_model import QWen3BModel
from langchain_core.messages import AIMessage, UsageMetadata

from Infrastructure.Utils.Logger import SingletonLogger

"""静态kv提取"""
MEMORY_PREFIX: list[str] = [

    "我叫",

    "我是",

    "我的职业是",

    "我喜欢",

    "我住在"
]


PROFILE_PATTERNS: list[str] = [

    "我叫",

    "我是",

    "我的名字是"
]


PREFERENCE_PATTERNS: list[str] = [

    "我喜欢",

    "我更喜欢",

    "我习惯"
]


PROJECT_PATTERNS: list[str] = [

    "我正在开发",

    "我正在做",

    "我的项目是",

    "目前在做"
]




"""使用docker vll本地部署的QWEN3B-AWQ模型进行kv提取"""
KV_PROMPT: str = """
你是key-value关系抽取器。

任务：

从用户输入中提取key-value关系



要求：

1 返回JSON

2 不要解释

3 importance范围1-10

4 可以返回多个key-value关系

5 严格按照给定的例子参考格式返回

例子：

输入：

我的名字叫张三，我来自CMU，我正在开发EveryoneAgent

输出：

{"items":
 [
     {
         "memory_type": "个人信息",
         "key": "名字",
         "value": "张三",
         "importance_level": 10
         
     },
     
     {
         "memory_type": "学校信息",
         "key": "学校",
         "value": "CMU",
         "importance_level": 8
     }，
     
     {
         "memory_type": "项目信息",
         "key": "项目",
         "value": "EveryoneAgent",
         "importance_level":7
     }
 ]
}

"""






class MemoryType(str, Enum):

    PROFILE = "profile"

    PREFERENCE = "preference"

    PROJECT = "project"
    
    


@dataclass
class MemoryItem(BaseModel):
    memory_type: str=""
    content: str="" 
    key:Optional[str]  =""  
    value:Optional[str]="" 
    importance_level: int = 0
    


class MemoryItemList(BaseModel):
    items: list[MemoryItem]



class MemoryExtractor:
    input_token: int = 0
    output_token: int = 0
    total_token: int = 0
    def __init__(self):
        pass
    @staticmethod
    async def get_token_used()->Tuple[int,int,int]:
        return MemoryExtractor.input_token,MemoryExtractor.output_token,MemoryExtractor.total_token
    
    @staticmethod
    async def extract_kv_memory_with_local_model(
        text: str
    ) -> MemoryItemList:
        messages: list = [
            ("system", KV_PROMPT),
            ("human", text)
        ]
        qwen3b_model: QWen3BModel = QWen3BModel()
        local_llm: ChatOpenAI=qwen3b_model.llm_local_qwen3B()
        result: AIMessage=await local_llm.ainvoke(messages)
        
        usage: UsageMetadata | None = result.usage_metadata
        # input_tokens = 系统提示词+用户输入总token（prompt）
        # output_tokens = 模型生成回答token（completion）
        # total_tokens = input + output
        assert usage is not None
        MemoryExtractor.input_token=usage.get("input_tokens",0)
        MemoryExtractor.output_token=usage.get("output_tokens",0)
        MemoryExtractor.total_token=usage.get("total_tokens",0)
                
        raw=result.content.strip() # type: ignore
        SingletonLogger().info(f"raw:{raw}")
        try:
            json_data = json.loads(raw)
            return MemoryItemList(**json_data)
        except Exception as e:
            SingletonLogger().error(e.__str__())
            return MemoryItemList(items=[])
        
    @staticmethod
    def extract_memory_simple(
        text: str
    ) -> str | None:
        """
        简单记忆提取
        """
        for prefix in MEMORY_PREFIX:

            if text.startswith(prefix):

                return text
        return None
    
    @staticmethod
    def _extract_content_memory(
        text: str
    ) -> list[MemoryItem]:
        memories: list[MemoryItem] = []
        for keyword in PROFILE_PATTERNS:

            if keyword in text:

                memories.append(

                    MemoryItem(
                        memory_type="profile",
                        content=text
                    )
                )
                break
            
        for keyword in PREFERENCE_PATTERNS:
            if keyword in text:
                memories.append(

                    MemoryItem(
                        memory_type="preference",
                        content=text
                    )
                )
                break

        for keyword in PROJECT_PATTERNS:

            if keyword in text:

                memories.append(

                    MemoryItem(
                        memory_type="project",
                        content=text
                    )
                )

                break
        return memories
    @staticmethod
    def _extract_kv_memory(
        text: str
    ) -> list[MemoryItem]:
        
        memories: list[MemoryItem] = []

        memories.extend(
            MemoryExtractor._extract_project(
                text
            )
        )

        memories.extend(
            MemoryExtractor._extract_skill(
                text
            )
        )

        memories.extend(
            MemoryExtractor._extract_goal(
                text
            )
        )
        
        memories.extend(
            MemoryExtractor._extract_persional_info(
                text
            )
        )

        return memories
    @staticmethod
    def _extract_project(
        text: str
    ) -> list[MemoryItem]:

        result: list[MemoryItem] = []

        patterns: list[str] = [
            r"我正在开发([^，。]+)",   
            r"我在做([^，。]+)",       
            r"当前项目是([^，。]+)"    
        ]

        for pattern in patterns:

            match: re.Match | None = re.search(
                pattern,
                text
            )

            if match:

                project_name: str = (
                    match.group(1)
                    .strip()
                )

                result.append(

                    MemoryItem(

                        memory_type="项目",

                        key="project",

                        value=project_name,

                        content=text
                    )
                )

        return result
    @staticmethod
    def _extract_skill(
        text: str
    ) -> list[MemoryItem]:

        result = []

        patterns = [
            r"我会(.+?)(，|。|$)",
            r"我熟悉(.+?)(，|。|$)",
            r"我掌握(.+?)(，|。|$)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                skill_name = (
                    match.group(1)
                    .strip()
                )

                result.append(

                    MemoryItem(

                        memory_type="擅长技能",

                        key="skill",

                        value=skill_name,

                        content=text
                    )
                )

        return result
    @staticmethod
    def _extract_goal(
        text: str
    ) -> list[MemoryItem]:

        result = []
        
        patterns = [
            r"我想([^，。]+)",
            r"未来我想([^，。]+)",
            r"我的目标是([^，。]+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                goal = (
                    match.group(1)
                    .strip()
                )

                result.append(

                    MemoryItem(

                        memory_type="生涯目标",

                        key="career_goal",

                        value=goal,

                        content=text
                    )
                )

        return result
    @staticmethod
    def _extract_persional_info(
        text: str
    ) -> list[MemoryItem]:
        result = []

        patterns = [
            r"我叫([^，。\s]+)",  
            r"我是([^，。\s]+)",
            r"我的名字是([^，。\s]+)"
            r"我爱吃([^，。\s]+)",
            r"我喜欢吃([^，。\s]+)"
        ]
        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                personal_info = (
                    match.group(1)
                    .strip()
                )

                result.append(

                    MemoryItem(

                        memory_type="个人信息",

                        key="name",

                        value=personal_info,

                        content=text
                    )
                )

        return result