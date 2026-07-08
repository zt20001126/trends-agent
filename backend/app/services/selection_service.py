from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.common.enums import SelectionTaskStatus
from app.common.exceptions import BusinessException
from app.repositories.selection_repository import SelectionRepository
from app.schemas.selection import (
    SelectionAnalyzeRequest,
    SelectionTaskDetailResponse,
    SelectionTaskResponse,
)


class SelectionService:
    """选品分析服务，负责任务创建、状态流转和结果聚合。"""

    def __init__(self, db_session: Session) -> None:
        self.repository = SelectionRepository(db_session)

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

