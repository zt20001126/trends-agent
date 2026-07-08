from fastapi import FastAPI

from app.api.v1.router import api_router
from app.common.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.settings import settings


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例，统一注册路由和异常处理。"""
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )
    app.include_router(api_router, prefix="/api/v1")
    register_exception_handlers(app)
    return app


app = create_app()
