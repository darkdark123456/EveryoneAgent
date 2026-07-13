OBSERVATION_PROMPT: str = """
你是AI助手。

用户问题：

{question}

你的思考：

{thought}

工具执行结果：

{observation}

请生成最终回答。

不要解释推理过程。

直接回答用户。
"""