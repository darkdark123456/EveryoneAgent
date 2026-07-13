from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException
)

from Infrastructure.Storage.database import (
    get_db
)

from Interfaces.Schemas.conversation import (
    CreateConversationRequest
)

from Infrastructure.Storage.crud import (
    get_messages_by_conversation
)

from sqlalchemy.orm import Session


"""
会话管理路由

负责：

1. 创建会话
2. 获取会话列表
3. 删除会话
4. 修改会话标题
"""

# FastAPI相关
from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException
)

# SQLAlchemy数据库会话
from sqlalchemy.orm import Session

# 获取数据库连接
from Infrastructure.Storage.database import (
    get_db
)

# CRUD方法
from Infrastructure.Storage.crud import (
    create_conversation,
    get_user_conversations,
    delete_conversation,
    rename_conversation,
    get_messages_by_conversation,
)


from Interfaces.Schemas.conversation import (
    CreateConversationRequest,
    ConversationResponse
)

from Infrastructure.Storage.models import (
   
    Conversation,
)

from Core.Memory.KV.memory_service import (
    
    load_messages
)

from Infrastructure.Storage.models import (
    Message
)


router: APIRouter = APIRouter(

    prefix="/conversation",

    tags=["历史对话"]
)


@router.post("/create")
async def create_new_conversation(
    request: Request,
    data: CreateConversationRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    创建新会话
    """

    user_id: int | None = request.session.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="请先登录"
        )

    conversation = create_conversation(
        db=db,
        user_id=user_id,
        title=data.title
    )

    return {
        "id": conversation.id,
        "title": conversation.title
    }
    
    
    
@router.get("/list")
async def get_conversation_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取当前用户会话列表
    """

    user_id: int | None = request.session.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="请先登录"
        )

    conversations: list[Conversation] = get_user_conversations(
        db=db,
        user_id=user_id
    )
    
  
    result: list[dict] = []

    title_str: str=""

    for conversation in conversations:
        
        if conversation.messages:
            first_message: str = conversation.messages[0].content
            title_str=first_message[:50]+"..."
        else:
            title_str="新会话"
        
        result.append(
            {
                "id": conversation.id,
                #"title": conversation.title,
                "title": title_str
            }
        )

    return result




@router.delete("/{conversation_id}")
async def remove_conversation(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    删除会话
    """

    user_id: int | None = request.session.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="请先登录"
        )

    delete_conversation(
        db=db,
        conversation_id=conversation_id
    )

    return {
        "message": "删除成功"
    }
    
    
    
    
@router.put("/{conversation_id}")
async def update_conversation_title(
    conversation_id: int,
    title: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    修改会话标题
    """

    user_id: int | None = request.session.get(
        "user_id"
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="请先登录"
        )

    rename_conversation(
        db=db,
        conversation_id=conversation_id,
        new_title=title
    )

    return {
        "message": "修改成功"
    }




@router.get(
    "/history/{conversation_id}"
)
async def get_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    messages: list[Message] = (
        
    get_messages_by_conversation(
        db=db,
        conversation_id=conversation_id
    )
    )
    
    return [

    {
        "role": message.role,
        "content": message.content
    }

    for message in messages
   ]