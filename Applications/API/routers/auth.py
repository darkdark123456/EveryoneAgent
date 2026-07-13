"""
认证路由
"""

from sqlalchemy.orm import Session

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from passlib.context import CryptContext

from Infrastructure.Storage.database import (
    get_db
)

from Infrastructure.Storage.crud import (
    get_user_by_email,
    create_user
)

from Interfaces.Schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse
)


router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["认证"]
)


pwd_context: CryptContext = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)



@router.post(
    "/register",
    response_model=UserResponse
)


async def register(
    request_data: RegisterRequest,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    用户注册
    """

    # 检查邮箱是否已存在
    existing_user = get_user_by_email(
        db,
        request_data.email
    )

    if existing_user:

        raise HTTPException(

            status_code=400,

            detail="邮箱已注册"
        )

    # 加密密码
    password_hash: str = (
        pwd_context.hash(
            request_data.password[:72]
        )
    )

    # 创建用户
    user = create_user(

        db=db,

        email=request_data.email,

        username=request_data.username,

        password_hash=password_hash
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username
    )
    
    
    
@router.post("/login")
async def login(
    request_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    用户登录
    """

    user = get_user_by_email(

        db,

        request_data.email
    )

    if not user:

        raise HTTPException(

            status_code=401,

            detail="用户不存在"
        )

    password_valid: bool = (
        pwd_context.verify(

            request_data.password,

            user.password_hash
        )
    )

    if not password_valid:

        raise HTTPException(

            status_code=401,

            detail="密码错误"
        )

    # Session存储用户ID
    request.session["user_id"] = user.id

    return {
        "message": "登录成功"
    }
    
    
    
async def get_current_user(
request: Request,
db: Session
)-> int:
    """
    获取当前登录用户
    """

    user_id: int | None = (
        request.session.get(
            "user_id"
        )
    )

    if user_id is None:

        raise HTTPException(

            status_code=401,

            detail="请先登录"
        )

    return user_id



@router.post("/logout")
async def logout(
    request: Request
) -> dict:
    """
    用户退出
    """

    request.session.clear()

    return {
        "message": "退出成功"
    }