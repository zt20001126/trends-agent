from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import BusinessException
from app.common.result import ApiResponse


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器，统一业务异常和未知异常的响应格式。"""

    @app.exception_handler(BusinessException)
    async def handle_business_exception(
        request: Request,
        exc: BusinessException,
    ) -> JSONResponse:
        # 业务异常只返回可理解的错误码和错误消息，不暴露内部实现细节。
        response = ApiResponse[None](code=exc.code, message=exc.message, data=None)
        return JSONResponse(status_code=exc.http_status, content=response.model_dump())

    @app.exception_handler(Exception)
    async def handle_unknown_exception(request: Request, exc: Exception) -> JSONResponse:
        # 未知异常统一转成系统错误，后续接入日志系统时在这里记录安全上下文。
        response = ApiResponse[None](code="SYSTEM_ERROR", message="系统异常", data=None)
        return JSONResponse(status_code=500, content=response.model_dump())

