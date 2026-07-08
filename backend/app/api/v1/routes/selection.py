from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.result import ApiResponse
from app.dependencies.database import get_database_session
from app.schemas.selection import (
    SelectionAnalyzeRequest,
    SelectionAnalyzeResponse,
    SelectionTaskDetailResponse,
)
from app.services.selection_service import SelectionService

router = APIRouter(prefix="/selections")


@router.post("/analyze", response_model=ApiResponse[SelectionAnalyzeResponse])
def analyze_selection(
    request: SelectionAnalyzeRequest,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionAnalyzeResponse]:
    """创建并执行选品分析任务。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.analyze(request))


@router.get("/{task_id}", response_model=ApiResponse[SelectionTaskDetailResponse])
def get_selection_task(
    task_id: UUID,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionTaskDetailResponse]:
    """查询选品分析任务详情。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.get_task_detail(task_id))

