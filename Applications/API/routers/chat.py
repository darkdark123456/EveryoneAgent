"""
1 使用本地QWEN3B小模型对用户的聊天进行kv和graph关系的提取
2 使用tongyi的大模型API对用户的问题进行回答
"""



from typing import Sequence

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends
)
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    BaseMessage,
    UsageMetadata
)


from pathlib import Path
import sys

from Capability.MCP.mcp_executor import MCPExecutor
from Core.Agent.agent_manager import AgentManager
from Core.Agent.agent_service import AgentRouterService
from Core.Memory.MemoryOrchestrator.memory_orcchestrator import MemoryOrchestrator
from Core.Memory.Message.memory_message_service import MessageMemoryService
from Core.Memory.Reflection.reflection_retriever import ReflectionRetriever
from Core.Planner.planner_executor import PlannerExecutor, ToolResult
from Core.Planner.planner_manager import PlannerManager
from Core.Planner.planner_models import PlannerResult
from Core.Planner.planner_service import PlannerService


ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT))

from Core.Memory.Reflection.reflection_manager import ReflectionManager
from Core.Memory.Graph.memory_graph_models import GraphRelation, GraphRelationList
from Core.Memory.Graph.memory_graph_service import GraphService

from Core.Memory.Graph.memory_graph_prompt import GraphPromptBuilder
from Core.Memory.Graph.memory_graph_retriever import GraphRetriever
from Core.Memory.Summary.summary_manager import SummaryManager

from Interfaces.Schemas.chat import (
    ChatRequest,
    ChatResponse
)

from Infrastructure.Storage.models import (
    ConversationSummary,
    Goal,
    MemoryGraph,
    Message,
    ReflectionMemory,
    UserMemory
)

from Core.Memory.KV.memory_manager import (
    load_memory
)

from Infrastructure.Storage.database import (
    get_db
)


from Infrastructure.Storage.crud import (
    get_messages_by_conversation,
    get_summary,
    load_summary,
    get_message_top_k,
)

from Core.Memory.KV.memory_service import (
    load_messages,
    save_memory,
    get_memories,
    _save_memory_by_importance,
)

from Core.Memory.KV.memory_importance_ruler import (
    MEMORY_IMPORTANCE_RULERS_DICT
)

from Core.Memory.KV.memory_retriever import (
    MemoryRetriever
)


from Core.Memory.KV.memory_extractor import MemoryExtractor,MemoryItem, MemoryItemList
from Core.Memory.Graph.memory_graph_extractor import GraphExtractor
from sqlalchemy.orm import Session
import asyncio 


from Knowledge.RAGPipeline.rag_service import (
    RAGService
)

from Core.Workflow.workflow_router      import WorkFlowQueryRouter
from Core.Workflow.workflow_tool_router import WorkFlowToolRouter
from Core.Workflow.workflow_router_type import WorkFlowRouteType
from Core.Workflow.workflow_tools_type  import WorkFlowToolType

from Core.Goal.goal_manager import GoalManager
from Applications.API.routers.top_prompt import get_top_prompt

from Infrastructure.Utils.Logger import SingletonLogger


from Infrastructure.Storage.crud import (
    create_message
)


from Knowledge.RAGPipeline.rag_query_route import (
    QueryRouter
)

from Applications.API.routers.llm_router_decision import LLMRouter,RouteDecision

from mcp.types import ListToolsResult
from mcp.types import CallToolResult



router: APIRouter = APIRouter(

    prefix="/chat",

    tags=["会话"]
)


@router.post(
    "",
    response_model=ChatResponse
)


async def chat(request_data: ChatRequest,request: Request,db: Session = Depends(get_db)) -> ChatResponse:
    
    """
    聊天接口
    """
    answer: str = ""
    
    user_id: int | None = (request.session.get("user_id"))
    
    if user_id is None:
        raise HTTPException(status_code=401,detail="请先登录")
    
    
    """将用户的聊天记录提取为kv结构化信息"""
    """使用本地的小模型进行提取"""
    #memory_items_old: list[MemoryItem] = MemoryExtractor._extract_kv_memory(request_data.message)
    
    memory_items: list[MemoryItem] = []
    
    kv_memory_list: MemoryItemList=await MemoryExtractor.extract_kv_memory_with_local_model(request_data.message)
    
    kv_input_token,kv_output_token,kv_total_token=await MemoryExtractor.get_token_used()
    SingletonLogger().info(f"Local QWen3B kv提取: input_token:{kv_input_token},output_token:{kv_output_token},total_token:{kv_total_token}")
    
    
    for kv_memory_item in kv_memory_list.items:
        memory_items.append(kv_memory_item)
        
    
    """判断当前用户的消息是否值得记忆，如果值得，根据重要性进行kv结构存储"""
    if memory_items.__len__()>0:
        SingletonLogger().info(f"当前用户的聊天消息值得存入长期记忆，正在保存...")
        for memory in memory_items:
           # memory.importance_level=MEMORY_IMPORTANCE_RULERS_DICT.get(memory.key if memory.key is not None else "other") # type: ignore
            SingletonLogger().info(f"保存记忆类型：{memory.memory_type},key：{memory.key},value：{memory.value},importance_level：{memory.importance_level}")
            _save_memory_by_importance(db=db,user_id=user_id,memory_type=memory.memory_type,
                                       content=memory.content,key=memory.key,value=memory.value, # type: ignore
                                       importance_level=memory.importance_level)

    """保存用户的聊天图关系"""
    """使用本地的小模型进行提取"""
    graph_result: GraphRelationList | None=await GraphExtractor._extract(request_data.message)
    
    
    graph_input_token,graph_output_token,graph_total_token=await GraphExtractor.get_token_used()
    SingletonLogger().info(f"QWen3B Local Graph提取: input_token:{graph_input_token},output_token:{graph_output_token},total_token:{graph_total_token}")
    
    
    if graph_result is None:
        graph_result=GraphRelationList()
    
    GraphService.save_relations(

        db=db,

        user_id=user_id,

        graph_relations= graph_result.relations
    )
    
    
    """获取当前用户的reflections"""
    reflections: list[ReflectionMemory] = (
        ReflectionRetriever
        .get_top_reflections(
            db,
            user_id
        )
    )
    
    """"构造reflection prompt"""
    reflection_prompt: str = ""
    for reflection in reflections:
        reflection_prompt += (
            f"[{reflection.reflection_type}]\n"
            f"{reflection.content}\n"
        )
    
        
    
    """加强的提示模板"""
    enhanced_prompt: str = ""
    """记忆提示模板"""
    memory_prompt:   str = ""
    """工作流路由类型"""
    workflow_route_type: WorkFlowRouteType = WorkFlowQueryRouter.route_from_json(request_data.message)
    """工作流路由摘要"""
    workflow_summary: str = ""
    """工作流路由用户reason"""
    workflow_reason: str = ""
    
    
    input_token:int=0
    output_token:int=0
    total_token:int=0
    """LLM动态路由"""
    if workflow_route_type == WorkFlowRouteType.UNKNOWN:
        SingletonLogger().info(f"静态路由规则表匹配失败，使用LLM动态路由")
        llm_route_type_res: RouteDecision=await LLMRouter.route(request.app.state.llm,request_data.message)
        workflow_route_type=WorkFlowRouteType(llm_route_type_res.route.lower())
        
        workflow_summary=llm_route_type_res.summary
        workflow_reason=llm_route_type_res.reason
        
        input_token,output_token,total_token=await LLMRouter.get_token_use()
        SingletonLogger().info(f"Online ChatTongyi LLM提取: input_token:{input_token},output_token:{output_token},total_token:{total_token}")
        
    
    """工作流路由 永远只能匹配一个路由 当用户的问题匹配到多个路由时，只匹配最高优先级的路由"""
    """当用户的问题被分解为多个子任务时候，后面的子任务会因为路由匹配而被忽略，如果使用下面的多任务模式，可以解决这个问题"""
    
    
    w_input_token:int=0
    w_output_token:int=0
    w_total_token:int=0
    
    f_input_token:int=0
    f_output_token:int=0
    f_total_token:int=0
    
    """" 使用本地QWEN0.7B embeding模型，进行vllm推理后，得到嵌入式向量 """
    match workflow_route_type:
        case WorkFlowRouteType.RAG:
            SingletonLogger().info("RAG Workflow...")
           # enhanced_prompt = RAGService.build_context(request_data.message)
           
           
           #openai的嵌入式向量额度用完了，调试代码使用下面民的一行
           #之后会接入本地QWEn0.7B的embeding模型，进行vllm推理后，得到嵌入式向量
            enhanced_prompt=request_data.message
            SingletonLogger().info(f"RAG enhanced prompt：{enhanced_prompt}")
            
            #为agent创建专属rag tools
            
        case WorkFlowRouteType.CHAT:
            SingletonLogger().info(f"CHAT Workflow...")
            enhanced_prompt = (request_data.message)
            
            #为agent创建专属chat tools
        
        case WorkFlowRouteType.MEMORY:
            SingletonLogger().info(f"MEMORY Workflow...")
            
            memories: list[UserMemory] = MemoryRetriever.get_user_memories_by_importance(
                db=db,
                user_id=user_id
            )
            
            memory_prompt = MemoryRetriever.build_memory_prompt(
                memories
            )
            
            enhanced_prompt=f"""{memory_prompt} 用户问题：{request_data.message}"""
        
        case WorkFlowRouteType.TOOL:
            SingletonLogger().info(f"TOOL Workflow...")
            enhanced_prompt=f"""你是一名{workflow_summary}方面的专家\n\n用户问题：{request_data.message}"""
            cur_tool_type: WorkFlowToolType = WorkFlowToolRouter.route(request_data.message)
            SingletonLogger().info(f"cur_tool_type：{cur_tool_type}")
            
            """匹配具体类型的tool，如果匹配到，用户的问题直接调用tool"""
            match cur_tool_type:
                case WorkFlowToolType.WEATHER:
                    tool_result: CallToolResult=await MCPExecutor.execute(
                        tool_name="query_weather",
                        city= ( await WorkFlowToolRouter.extract_address(request_data.message)).get("city") # type: ignore
                    )
                    SingletonLogger().info(f"tool_result：{tool_result}")
                    w_input_token,w_output_token,w_total_token=await WorkFlowToolRouter.get_token_use()
                    SingletonLogger().info(f"Local QWen3B tool提取: input_token:{w_input_token},output_token:{w_output_token},total_token:{w_total_token}")
                    
                    #answer=tool_result.structuredContent["result"] # type: ignore
               
                case WorkFlowToolType.FILE:
                    tool_result: CallToolResult=await MCPExecutor.execute(
                        tool_name="write_file",
                        content= ( await WorkFlowToolRouter.write_file(request_data.message)).get("content") # type: ignore
                    )
                    SingletonLogger().info(f"tool_result：{tool_result}")
                    f_input_token,f_output_token,f_total_token=await WorkFlowToolRouter.get_token_use()
                    SingletonLogger().info(f"Local QWen3B tool提取: input_token:{f_input_token},output_token:{f_output_token},total_token:{f_total_token}")
                    #answer=tool_result.structuredContent["result"] # type: ignore
                case _:
                    pass       
        case _:
            enhanced_prompt = (request_data.message)
    
    """"细粒度更高的tool查找"""
    """多任务划分，将用户的问题划分为多个子任务，每个子任务如果有对应的tool，可以直接调用，api不走agent，获得的结果更精准"""
    """如果没有对应的tool，可以判断是否有对应的agent可以调用，如果有，可以调用，走agent，获得的结果更全面"""
    """如果没有对应的agent，使用普通的llm agent进行回答，这取决于对应模型的好坏"""
    planner_list: list[PlannerResult]=await PlannerService.generate_plan(request_data.message)
    
    p_input_token,p_output_token,p_total_token=await PlannerService.get_token_use()
    SingletonLogger().info(f"Generate Plan Online Tongyi提取: input_token:{p_input_token},output_token:{p_output_token},total_token:{p_total_token}")
    
    answer: str = ""
    
    plan_tool_results: list[ToolResult]=await PlannerExecutor.execute_plan(planner_list)
    
    

    """收集多任务划分对应不同tool的执行结果"""    
    answer+=await PlannerExecutor.collect_plan_results(plan_tool_results)
    
    
    a_input_token:int=0
    a_output_token: int=0
    a_total_token: int=0
    """细粒度没那么高的agent查找"""
    """如果没有对应的tool 或者 对应的tool结果返回了空，那么使用带有tool的agent进行回答"""
    if answer=="":
            
        """"创建对应的agent，如果没有对应的agent，则创建默认的agent"""
        """目前支持四种agent，travel_agent,weather_agent,document_agent,general_agent"""
        """它们可以协同工作"""
        #agent_type_result_list: list[dict[str,str]]=await AgentRouterService.route(query=request_data.message)
        #agent_list: list[CompiledStateGraph]=await AgentManager.get_agent_list(agent_type_list=agent_type_result_list)
        res: list[dict[str,str]] =  await AgentRouterService.get_plann_agent_reference( await PlannerService.get_planner_str())
        a_input_token,a_output_token,a_total_token=await AgentRouterService.get_token_use()
        SingletonLogger().info(f"Agent Router Online Tongyi提取: input_token:{a_input_token},output_token:{a_output_token},total_token:{a_total_token}")
        
        answer=await AgentManager.agent_excutor_planner(result=res)
        
        
    """获得当前用户聊天和之前聊天的所有实体"""
    entities: set=set()
    for item in graph_result.relations:
        entities.add(item.source)
        entities.add(item.target)
  
    graph_relations: list[MemoryGraph] =[]
    
    for entity in entities:
        cur_graph_relations: list[MemoryGraph] = GraphRetriever.get_entity_relations(
            db=db,
            user_id=user_id,
            entity_name=entity
        )
        graph_relations.extend(cur_graph_relations)
    
    
    """去重实体之间的图关系"""
    id_set: set = set()
    unique_relations: list[MemoryGraph] = []
    for relation in graph_relations:
        if relation.id not in id_set:
            unique_relations.append(relation)
            id_set.add(relation.id)

    
    
    """"构造graph prompt"""
    graph_prompt: str = (

    GraphPromptBuilder.build(

        unique_relations
    )
    )
    
    
    """构造召回prompt"""
    recall_prompt: str =MemoryOrchestrator.build_prompt(
        db=db,
        user_id=user_id,
        conversation_id=request_data.conversation_id,
        query=request_data.message
    )
    
    

    """加载聊天记录 随着用户的聊天记录越来越多，消耗token的数量会急剧增加"""     
    conversation_id: int = request_data.conversation_id
    history_message:list[BaseMessage] = await asyncio.to_thread(load_messages,db,conversation_id)
    
    """加载聊天摘要"""
    histroy_summary:list[BaseMessage] = await asyncio.to_thread(load_summary,db,conversation_id) # type: ignore
    

    """构造top-k message prompt，让模型得到更多的上下文信息"""
    message_top_k_prompt: str=await MessageMemoryService.build_prompt(db=db,conversation_id=conversation_id)
    

    """加载agent"""
    agent:CompiledStateGraph = request.app.state.agent
    
    """"组合prompt"""
    
    """组合消息"""
    # all_messages: list[BaseMessage] = ([SystemMessage(content=memory_prompt)]+
    #                                    histroy_summary+
    #                                    [SystemMessage(content=graph_prompt)]+
    #                                    [SystemMessage(content=reflection_prompt)]+
    #                                    [HumanMessage(content=enhanced_prompt)])
    
    
    """组合消息 使用了召回prompt 减少token消耗"""
    all_messages: Sequence[BaseMessage] = ([SystemMessage(content=get_top_prompt())]+ #顶层prompt 规范llm的行为
                                           [SystemMessage(content=message_top_k_prompt)]+#最近top-k消息形成的prompt
                                           [SystemMessage(content=recall_prompt)] #召回prompt
                                           +[HumanMessage(content=enhanced_prompt)])#增强版本的用户的问题
    
    """保存用户消息"""
    create_message(

        db=db,

        conversation_id=conversation_id,

        role="用户",

        content=request_data.message
    )
    
    
    r_input_token: int=0
    r_output_token: int=0
    r_total_token: int=0
    """兜底措施，如果最终没有找到合适的工具进行调用，直接调用通用agent"""
    if answer == "":
        """调用agent"""
        result: dict = await agent.ainvoke(

            {
                "messages": all_messages
            },

            config={"configurable": {"thread_id": str(conversation_id)}}
        )

        msg_list: list[BaseMessage] = result.get("messages", [])
        ai_message: AIMessage = msg_list[-1] # type: ignore
        answer: str= ai_message.content # type: ignore
        meta: dict=ai_message.response_metadata # type: ignore
        usage: dict = meta.get("token_usage", {})
  
        r_input_token:int=usage.get("input_tokens",0)
        r_output_token: int=usage.get("output_tokens",0)
        r_total_token: int=usage.get("total_tokens",0)
        SingletonLogger().info(f"Online Tongyi: input_token:{r_input_token} output_token:{r_output_token} total_token:{r_total_token}")
        
    """保存AI消息"""
    create_message(

        db=db,

        conversation_id=conversation_id,

        role="E-Agent",

        content=answer
    )
    
    
    """更新摘要"""
    await SummaryManager.check_and_update_summary(
        
        db=db,
        conversation_id=conversation_id
    )
    
    
    
    """更新反思"""
    await ReflectionManager.check_and_update_reflection(
        
        db=db,
        conversation_id=
        conversation_id,
        user_id=user_id
    )
    
    
    """更新目标"""
    await GoalManager.check_and_update_goal(
        
        db=db,
        conversation_id=conversation_id,
        user_id=user_id
    )

    T: int=(kv_total_token+graph_total_token+total_token+f_total_token+w_total_token+p_total_token+a_total_token+r_total_token)
    A: int=(kv_total_token+graph_total_token+w_total_token+f_total_token)
    
    if T!=0:
        W: float=A/T
        print(W)
        #0.1172
    return ChatResponse(

        response=answer
    )