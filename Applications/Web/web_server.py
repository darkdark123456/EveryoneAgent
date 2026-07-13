"""
Web页面服务

负责：

1. HTML页面渲染
2. 页面跳转
3. Session检查
"""

from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse
from fastapi.responses import Response

from fastapi.templating import (
    Jinja2Templates
)

from pathlib import Path

# 创建Router
router: APIRouter = APIRouter()

# 模板目录
BASE_DIR: Path = Path(__file__).parent  # 当前文件所在目录：Applications/Web/
templates: Jinja2Templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/login")
async def login_page(request: Request) ->  HTMLResponse:
    """
    登录页面
    """

    return templates.TemplateResponse(request=request,
                                      name="login.html",
                                      context=
                                    {
                                        "request": request
                                    }
    )
    


@router.get("/register")
async def register_page(
    request: Request
)-> HTMLResponse:
    """
    注册页面
    """

    return templates.TemplateResponse(request=request,
                                      name="register.html",
                                      context=

                                        {
                                            "request": request
                                        }
    )
    
    
@router.get("/chat")
async def chat_page(
    request: Request
)-> Response:
    """
    聊天页面
    """

    user_id = request.session.get(
        "user_id"
    )

    # 未登录
    if user_id is None:

        return RedirectResponse(
            "/login"
        )

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context=
        {
            "request": request
        }
    )
    
__all__ = [
    "router"
]