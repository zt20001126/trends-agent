from fastapi import APIRouter

from app.common.result import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict[str, str]])
def health_check() -> ApiResponse[dict[str, str]]:
    """健康检查接口，仅返回应用可用状态。"""
    return ApiResponse(data={"status": "ok"})

