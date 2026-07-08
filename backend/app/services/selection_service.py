from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.workflow.selection_graph import SelectionWorkflow
from app.common.enums import SelectionTaskStatus
from app.common.exceptions import BusinessException
from app.repositories.selection_repository import SelectionRepository
from app.schemas.selection import (
    BatchSelectionAnalyzeRequest,
    BatchSelectionAnalyzeResponse,
    SelectionAnalyzeResponse,
    SelectionAnalyzeRequest,
    SelectionTaskListResponse,
    SelectionTaskDetailResponse,
    SelectionTaskResponse,
)


class SelectionService:
    """选品分析服务，负责任务创建、状态流转和结果聚合。"""

    def __init__(self, db_session: Session, workflow: SelectionWorkflow | None = None) -> None:
        self.db_session = db_session
        self.repository = SelectionRepository(db_session)
        self.workflow = workflow or SelectionWorkflow()

    def create_task(self, request: SelectionAnalyzeRequest) -> SelectionTaskResponse:
        """创建选品分析任务。

        Step 1: 校验请求数据已经由 Pydantic 完成。
        Step 2: 写入 pending 状态任务，等待后续 Agent 工作流消费。
        Step 3: 返回任务基础信息，避免 API 层感知 ORM 模型。
        """
        task = self.repository.create_task(
            keyword=request.keyword,
            country=request.country,
            language=request.language,
            status=SelectionTaskStatus.PENDING.value,
        )
        return SelectionTaskResponse.model_validate(task)

    def analyze(self, request: SelectionAnalyzeRequest) -> SelectionAnalyzeResponse:
        """执行完整选品分析。

        Step 1: 创建 pending 任务并切换为 running。
        Step 2: 调用 LangGraph 工作流完成 Skill 编排和结果持久化。
        Step 3: 提交事务并返回 Markdown 报告。
        """
        task = self.repository.create_task(
            keyword=request.keyword,
            country=request.country,
            language=request.language,
            status=SelectionTaskStatus.PENDING.value,
        )
        self.repository.update_task_status(task=task, status=SelectionTaskStatus.RUNNING.value)

        try:
            final_state = self.workflow.run(
                task_id=task.id,
                keyword=task.keyword,
                country=task.country,
                language=task.language,
                repository=self.repository,
            )
            self.db_session.commit()
        except Exception as exc:
            self.db_session.rollback()
            failed_task = self.repository.get_task(task.id)
            if failed_task is not None:
                self.repository.update_task_status(
                    task=failed_task,
                    status=SelectionTaskStatus.FAILED.value,
                    error_message=str(exc),
                )
                self.db_session.commit()
            raise

        task_detail = self.get_task_detail(task.id)
        return SelectionAnalyzeResponse(
            task_id=task.id,
            status=task_detail.task.status,
            report=final_state["report"].markdown_content,
        )

    def create_pending_task(self, request: SelectionAnalyzeRequest) -> SelectionTaskResponse:
        """创建异步选品分析任务。

        Step 1: 写入 pending 状态任务。
        Step 2: 提交事务，让后台任务可以独立读取。
        Step 3: 返回任务基础信息给 API 层。
        """
        task = self.repository.create_task(
            keyword=request.keyword,
            country=request.country,
            language=request.language,
            status=SelectionTaskStatus.PENDING.value,
        )
        self.db_session.commit()
        return SelectionTaskResponse.model_validate(task)

    def run_existing_task(self, task_id: UUID) -> None:
        """执行已创建的异步分析任务。"""
        task = self.repository.get_task(task_id)
        if task is None:
            raise BusinessException(message="选品分析任务不存在", code="SELECTION_TASK_NOT_FOUND", http_status=404)

        self.repository.update_task_status(task=task, status=SelectionTaskStatus.RUNNING.value)
        try:
            self.workflow.run(
                task_id=task.id,
                keyword=task.keyword,
                country=task.country,
                language=task.language,
                repository=self.repository,
            )
            self.db_session.commit()
        except Exception as exc:
            self.db_session.rollback()
            failed_task = self.repository.get_task(task_id)
            if failed_task is not None:
                self.repository.update_task_status(
                    task=failed_task,
                    status=SelectionTaskStatus.FAILED.value,
                    error_message=str(exc),
                )
                self.db_session.commit()
            raise

    def analyze_batch(self, request: BatchSelectionAnalyzeRequest) -> BatchSelectionAnalyzeResponse:
        """批量执行选品分析。"""
        results = [
            self.analyze(
                SelectionAnalyzeRequest(
                    keyword=keyword,
                    country=request.country,
                    language=request.language,
                )
            )
            for keyword in request.keywords
        ]
        return BatchSelectionAnalyzeResponse(results=results)

    def list_tasks(self, limit: int, offset: int) -> SelectionTaskListResponse:
        """分页查询历史选品分析任务。"""
        tasks = self.repository.list_tasks(limit=limit, offset=offset)
        return SelectionTaskListResponse(
            items=[SelectionTaskResponse.model_validate(task) for task in tasks],
            limit=limit,
            offset=offset,
        )

    def get_task_detail(self, task_id: UUID) -> SelectionTaskDetailResponse:
        """查询选品分析任务详情。

        Step 1: 查询任务主记录，不存在时抛出业务异常。
        Step 2: 聚合各类最新分析结果和报告。
        Step 3: 转换为 API 详情响应对象。
        """
        task = self.repository.get_task(task_id)
        if task is None:
            raise BusinessException(message="选品分析任务不存在", code="SELECTION_TASK_NOT_FOUND", http_status=404)

        return SelectionTaskDetailResponse(
            task=SelectionTaskResponse.model_validate(task),
            trend_result=self._model_to_dict(self.repository.get_latest_trend_result(task_id)),
            product_result=self._model_to_dict(self.repository.get_latest_product_result(task_id)),
            review_result=self._model_to_dict(self.repository.get_latest_review_result(task_id)),
            score_result=self._model_to_dict(self.repository.get_latest_score_result(task_id)),
            report=self._model_to_dict(self.repository.get_latest_report(task_id)),
        )

    @staticmethod
    def _model_to_dict(model: object | None) -> dict[str, Any] | None:
        """将 ORM 模型转换为字典，避免响应层直接暴露 SQLAlchemy 对象。"""
        if model is None:
            return None

        return {
            column.name: getattr(model, column.name)
            for column in model.__table__.columns  # type: ignore[attr-defined]
        }


def run_selection_analysis_background(task_id: UUID) -> None:
    """后台执行选品分析任务，作为 MVP 级异步任务队列入口。"""
    from app.db.session import SessionLocal

    db_session = SessionLocal()
    try:
        SelectionService(db_session).run_existing_task(task_id)
    finally:
        db_session.close()
