from typing import Any, TypedDict
from uuid import UUID

from app.repositories.selection_repository import SelectionRepository
from app.schemas.selection import (
    ProductResultDTO,
    ReportDTO,
    ReviewResultDTO,
    ScoreResultDTO,
    TrendResultDTO,
)


class SelectionState(TypedDict, total=False):
    """选品分析工作流状态，用于在 LangGraph 节点之间传递上下文。"""

    task_id: UUID
    keyword: str
    normalized_keyword: str
    country: str
    language: str
    repository: SelectionRepository
    planned_steps: list[str]
    trend_result: TrendResultDTO
    product_result: ProductResultDTO
    review_result: ReviewResultDTO
    score_result: ScoreResultDTO
    report: ReportDTO
    errors: list[dict[str, Any]]

