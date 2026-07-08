from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.common.result import ApiResponse
from app.dependencies.database import get_database_session
from app.schemas.selection import (
    BatchSelectionAnalyzeRequest,
    BatchSelectionAnalyzeResponse,
    SelectionAnalyzeRequest,
    SelectionAnalyzeResponse,
    SelectionTaskListResponse,
    SelectionTaskDetailResponse,
)
from app.services.selection_service import SelectionService, run_selection_analysis_background

router = APIRouter(prefix="/selections")


@router.post("/analyze", response_model=ApiResponse[SelectionAnalyzeResponse])
def analyze_selection(
    request: SelectionAnalyzeRequest,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionAnalyzeResponse]:
    """创建并执行选品分析任务。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.analyze(request))


@router.post("/analyze-async", response_model=ApiResponse[SelectionAnalyzeResponse])
def analyze_selection_async(
    request: SelectionAnalyzeRequest,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionAnalyzeResponse]:
    """创建异步选品分析任务，并交给后台任务执行。"""
    service = SelectionService(db_session)
    task = service.create_pending_task(request)
    background_tasks.add_task(run_selection_analysis_background, task.id)
    return ApiResponse(
        data=SelectionAnalyzeResponse(
            task_id=task.id,
            status=task.status,
            report=None,
        )
    )


@router.post("/batch-analyze", response_model=ApiResponse[BatchSelectionAnalyzeResponse])
def batch_analyze_selection(
    request: BatchSelectionAnalyzeRequest,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[BatchSelectionAnalyzeResponse]:
    """批量执行选品分析任务。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.analyze_batch(request))


@router.get("", response_model=ApiResponse[SelectionTaskListResponse])
def list_selection_tasks(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionTaskListResponse]:
    """分页查询选品分析历史任务。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.list_tasks(limit=limit, offset=offset))


@router.get("/{task_id}", response_model=ApiResponse[SelectionTaskDetailResponse])
def get_selection_task(
    task_id: UUID,
    db_session: Session = Depends(get_database_session),
) -> ApiResponse[SelectionTaskDetailResponse]:
    """查询选品分析任务详情。"""
    service = SelectionService(db_session)
    return ApiResponse(data=service.get_task_detail(task_id))
