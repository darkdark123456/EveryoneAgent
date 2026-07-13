from datetime import datetime

from sqlalchemy.orm import Session

from Core.Goal.goal_models import GoalResult
from Infrastructure.Storage.models import (
    ConversationSummary,
    Goal,
    MemoryGraph,
    ReflectionMemory,
    ReflectionState,
    User,
    Conversation,
    Message,
    UserMemory
)


from langchain_core.messages import BaseMessage, HumanMessage
from Core.Memory.KV.memory_ranker import MemoryRanker

max_count: int =4

def get_user_by_email(
    db: Session,
    email: str
) -> User | None:
    """
    根据邮箱查询用户
    """

    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )
    

def create_user(
    db: Session,
    email: str,
    username: str,
    password_hash: str
    ) -> User:
    """
    创建用户
    """

    user: User = User(

        email=email,

        username=username,

        password_hash=password_hash

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user

def create_conversation(
    db: Session,
    user_id: int,
    title: str
) -> Conversation:
    """
    创建会话
    """

    conversation: Conversation = Conversation(

        user_id=user_id,

        title=title
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


def get_user_conversations(
    db: Session,
    user_id: int
) -> list[Conversation]:
    """
    获取用户全部会话
    """

    return (

        db.query(Conversation)

        .filter(
            Conversation.user_id
            ==
            user_id
        )

        .filter(
            Conversation.is_deleted
            ==
            False
        )

        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

def delete_conversation(
    db: Session,
    conversation_id: int
) -> None:
    """
    删除会话
    """

    conversation = (

        db.query(Conversation)

        .filter(
            Conversation.id
            ==
            conversation_id
        )

        .first()
    )

    if conversation:

        conversation.is_deleted = True

        db.commit()
       
       
        
def rename_conversation(
    db: Session,
    conversation_id: int,
    new_title: str
) -> None:
    """
    修改会话标题
    """

    conversation = (

        db.query(Conversation)

        .filter(
            Conversation.id
            ==
            conversation_id
        )

        .first()
    )

    if conversation:

        conversation.title = new_title

        db.commit()



def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    保存消息
    """

    message: Message = Message(

        conversation_id=conversation_id,

        role=role,

        content=content
    )

    db.add(message)

    db.commit()

    db.refresh(message)

    return message



def get_messages_by_conversation(
    db: Session,
    conversation_id: int
) -> list[Message]:
    """
    获取会话历史
    """

    return (

        db.query(Message)

        .filter(
            Message.conversation_id
            ==
            conversation_id
        )

        .order_by(
            Message.created_at.desc()
        )
        .all()
    )



def get_recent_messages(
    db: Session,
    conversation_id: int,
    max_message_count: int
) -> list[Message]:
    """
    获取会话最近消息
    """

    return (

        db.query(Message)

        .filter(
            Message.conversation_id
            ==
            conversation_id
        )

        .order_by(
            Message.created_at.desc()
        )
        .limit(max_message_count)
        .all()
    )
    
def _update_memory_by_importance(
    db: Session,
    user_id: int,
    memory_type: str,
    key: str,
    value: str,
    importance: int
) -> UserMemory:
    """
    新增或更新记忆
    """
    memory: UserMemory | None = (

        db.query(UserMemory)

        .filter(
            UserMemory.user_id == user_id
        )

        .filter(
            UserMemory.memory_key == key
        )

        .first()
    )
    
    if memory:
        memory.memory_value = value
        memory.importance = importance
        memory.access_count += 1
        memory.score=MemoryRanker.score(memory)
        
        memory.last_access_time=datetime.now()
        db.commit()
        db.refresh(memory)
        return memory
    else:
        memory = UserMemory(
        user_id=user_id,
        memory_type=memory_type,
        memory_key=key,
        memory_value=value,
        importance=importance,
        access_count=1,
        updated_at=datetime.now(),
        last_access_time=datetime.now()  
    )
        memory.score=MemoryRanker.score(memory)
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory



async def get_message_top_k(
    db: Session,
    conversation_id: int,
    top_k: int
) -> list[Message]:
    """
    获取会话最近消息
    """

    return (

        db.query(Message)

        .filter(
            Message.conversation_id
            ==
            conversation_id
        )

        .order_by(
            Message.created_at.desc()
        )
        .limit(top_k)
        .all()
)




def get_message_count(
    db: Session,
    conversation_id: int
) -> int:
    """
    获取会话消息总数
    """

    return (

        db.query(Message)

        .filter(
            Message.conversation_id
            ==
            conversation_id
        )

        .count()
    )
    
    
def get_summary(
    db: Session,
    conversation_id: int
) -> ConversationSummary | None:
    """
    获取会话摘要
    """

    return (

        db.query(
            ConversationSummary
        )

        .filter(
            ConversationSummary.conversation_id
            ==
            conversation_id
        )

        .first()
    )
    

def load_user_memory(
    db: Session,
    user_id: int
)-> list[UserMemory]:
    """
    加载历史记忆
    """
    return (

        db.query(UserMemory)

        .filter(
            UserMemory.user_id
            ==
            user_id
        )
        .order_by(
            UserMemory.importance.desc()
        )
        
        .all()
    )






def load_summary(db: Session, conversation_id: int) -> list[BaseMessage]:
    summary: ConversationSummary | None = get_summary(db, conversation_id)
    
    histroy_summary: list[BaseMessage] = []
    
    if summary is None:
        return histroy_summary
    histroy_summary.append(HumanMessage(content=summary.summary)) # type: ignore
    return histroy_summary
        

def save_or_update_summary(
    db: Session,
    conversation_id: int,
    summary: str,
    last_message_count: int
) -> None:
    """
    保存或更新摘要
    """

    record = (

        db.query(
            ConversationSummary
        )

        .filter(
            ConversationSummary.conversation_id
            ==
            conversation_id
        )

        .first()
    )

    if record is None:

        record = ConversationSummary(

            conversation_id=
            conversation_id,

            summary=
            summary,

            last_message_count=
            last_message_count
        )

        db.add(record)

    else:

        record.summary = summary # type: ignore

        record.last_message_count = ( # type: ignore
            last_message_count
        )

    db.commit()
    db.refresh(record)
    






def get_reflection_state(
    db: Session,
    conversation_id: int
) -> ReflectionState | None:

    return (
        db.query(
            ReflectionState
        )
        .filter(
            ReflectionState.conversation_id
            ==
            conversation_id
        )
        .first()
    )



async def update_reflection_state(
    db: Session,
    conversation_id: int,
    current_count: int
) -> None:
    state: ReflectionState | None = get_reflection_state(
    db,
    conversation_id
    )
    if state:

        state.last_reflection_count = (
            current_count
        )
    else:
        state = ReflectionState(

        conversation_id=
        conversation_id,

        last_reflection_count=
        current_count
    )

        db.add(state)
        
        
    db.commit()
    
    
def get_graph_memories(
    db: Session,
    user_id: int
) -> list[MemoryGraph] | None:

    return (
        db.query(
            MemoryGraph
        )
        .filter(
            MemoryGraph.user_id
            ==
            user_id    
        )
        .all()
    )
    
    

    
def reflection_exists(
    db: Session,
    user_id: int,
    reflection_type: str,
    content: str
):
    return (
        db.query(ReflectionMemory)
        .filter(
            ReflectionMemory.user_id
            ==
            user_id
        )
        .filter(
            ReflectionMemory.reflection_type
            ==
            reflection_type
        )
        .filter(
            ReflectionMemory.content
            ==
            content
        )
        .first()
    )
 
 
    
async def save_goal(
    db: Session,
    user_id: int,
    goal_result: GoalResult,
    reflection_count: int=0
) -> None:
    goal: Goal = Goal(

    user_id=user_id,

    goal_type=
    goal_result.goal_type,

    title=
    goal_result.title,

    description=
    goal_result.description,

    last_reflection_count=
    reflection_count,
    
    
    confidence=
    goal_result.confidence,

    importance=
    goal_result.importance,

    progress=0,

    status="active"
)
    
    db.add(goal)

    db.commit()

    db.refresh(goal)


async def get_active_goal(
    db: Session,
    user_id: int
) -> Goal | None:
    return (

    db.query(Goal)

    .filter(

        Goal.user_id
        ==
        user_id,

        Goal.status
        ==
        "active"
    )

    .order_by(
        Goal.importance.desc()
    )

    .first()
)
    
    
async def update_goal(
    db: Session,
    goal_id: int,
    confidence: float,
    importance: int,
    description: str,
    reflection_count: int=0
):
    goal: Goal | None = (

    db.query(Goal)

    .filter(
        Goal.id
        ==
        goal_id
    )

    .first()
)
    if goal is None:
        return
    
    goal.confidence = confidence

    goal.importance = importance

    goal.description = description

    goal.last_reflection_count = reflection_count

    db.commit()
    
    
async def get_reflection_count(
    db: Session,
    user_id: int
) -> int:

    return (
        db.query(
            ReflectionMemory
        )

        .filter(
            ReflectionMemory.user_id
            ==
            user_id
        )

        .count()
    )
    
async def get_last_goal_reflection_count(
    db: Session,
    user_id: int
) -> int:

    goal: Goal | None = (

        db.query(Goal)

        .filter(

            Goal.user_id
            ==
            user_id,

            Goal.status
            ==
            "active"
        )

        .first()
    )

    if goal is None:

        return 0

    return (
        goal.last_reflection_count
    )