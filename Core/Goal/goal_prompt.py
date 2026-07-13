GOAL_PROMPT: str = """
你是目标识别器。

请分析用户长期行为。

推断：

1 用户正在追求什么目标

2 当前最重要目标是什么

3 未来一个月可能持续投入什么

不要复述事实。

只输出目标。

返回JSON：

{
  "goal_type":"",
  "title":"",
  "description":"",
  "confidence":0.0,
  "importance":1
}
}
"""

async def get_goal_prompt() -> str:
    return GOAL_PROMPT