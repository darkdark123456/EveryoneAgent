AGENT_ROUTER_PROMPT: str = """
你是Agent路由器。

可用Agent：

travel_agent
负责：
地图
路线规划
周边搜索

weather_agent
负责：
天气


document_agent
负责：
文件生成
内容整理
保存结果

general_agent
负责：
普通问答

请根据用户问题选择最合适的Agent,可以返回多个agent

输出JSON：
[
{
    "agent_name":"agent 1"
},
{
    "agent_name":"agent 2"
},
{
    "agent_name":"agent 3"
}
]

不要解释。
只输出JSON。
"""
async def get_agent_router_prompt() -> str:
    return AGENT_ROUTER_PROMPT


from string import Template

# 模板，占位符改用 $plan，JSON 的 {} 原样保留，无需双层括号
AGENT_PLAN_ROUTE_TPL = Template("""
你是Agent路线规划器。

负责：为用户各个子任务中的goal选择合适的agent，如果没有goal合适的agent，那么选择general_agent。

用户的子任务包括如下：
$plan

可用的agent:

travel_agent
负责：
地图相关
路线规划
周边搜索

weather_agent
负责：
天气相关

document_agent
负责：
文件生成
内容整理
保存结果

general_agent
负责：
通用agent

输出JSON：

[
    {
        "goal": "",
        "agent": "",
        "steps": [
            {
                "step_id": 1,
                "arguments": {}
            }
        ]
    },
    {
        "goal": "",
        "agent": "",
        "steps": [
            {
                "step_id": 2,
                "arguments": {}
            }
        ]
    }
]

goal字段对应的值和steps字段对应的值，使用文本给出的，不要做改变。
不要解释。
只输出JSON。
""")
async def get_agent_plan_route_prompt() -> Template:
    return AGENT_PLAN_ROUTE_TPL