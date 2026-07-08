from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product_result import ProductResult
from app.models.report import Report
from app.models.review_result import ReviewResult
from app.models.score_result import ScoreResult
from app.models.selection_task import SelectionTask
from app.models.trend_result import TrendResult
from app.schemas.selection import (
    ProductResultDTO,
    ReportDTO,
    ReviewResultDTO,
    ScoreResultDTO,
    TrendResultDTO,
)


class SelectionRepository:
    """选品分析 Repository，封装任务和分析结果的数据库读写。"""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def create_task(
        self,
        keyword: str,
        country: str,
        language: str,
        status: str,
    ) -> SelectionTask:
        """创建选品分析任务。"""
        task = SelectionTask(
            keyword=keyword,
            country=country,
            language=language,
            status=status,
        )
        self.db_session.add(task)
        self.db_session.flush()
        return task

    def get_task(self, task_id: UUID) -> SelectionTask | None:
        """根据任务 ID 查询选品分析任务。"""
        statement = select(SelectionTask).where(SelectionTask.id == task_id)
        return self.db_session.scalar(statement)

    def list_tasks(self, limit: int, offset: int) -> list[SelectionTask]:
        """分页查询选品分析任务历史。"""
        statement = select(SelectionTask).order_by(SelectionTask.created_at.desc()).limit(limit).offset(offset)
        return list(self.db_session.scalars(statement))

    def update_task_status(
        self,
        task: SelectionTask,
        status: str,
        error_message: str | None = None,
        normalized_keyword: str | None = None,
    ) -> SelectionTask:
        """更新任务状态、错误信息和归一化关键词。"""
        task.status = status
        task.error_message = error_message
        if normalized_keyword is not None:
            task.normalized_keyword = normalized_keyword
        self.db_session.flush()
        return task

    def save_trend_result(self, task_id: UUID, result: TrendResultDTO) -> TrendResult:
        """保存趋势分析结果。"""
        trend_result = TrendResult(task_id=task_id, **result.model_dump())
        self.db_session.add(trend_result)
        self.db_session.flush()
        return trend_result

    def save_product_result(self, task_id: UUID, result: ProductResultDTO) -> ProductResult:
        """保存商品竞品分析结果。"""
        product_result = ProductResult(task_id=task_id, **result.model_dump())
        self.db_session.add(product_result)
        self.db_session.flush()
        return product_result

    def save_review_result(self, task_id: UUID, result: ReviewResultDTO) -> ReviewResult:
        """保存评论痛点分析结果。"""
        review_result = ReviewResult(task_id=task_id, **result.model_dump())
        self.db_session.add(review_result)
        self.db_session.flush()
        return review_result

    def save_score_result(self, task_id: UUID, result: ScoreResultDTO) -> ScoreResult:
        """保存选品机会评分结果。"""
        score_result = ScoreResult(task_id=task_id, **result.model_dump())
        self.db_session.add(score_result)
        self.db_session.flush()
        return score_result

    def save_report(self, task_id: UUID, report: ReportDTO) -> Report:
        """保存 Markdown 选品报告。"""
        report_result = Report(task_id=task_id, **report.model_dump())
        self.db_session.add(report_result)
        self.db_session.flush()
        return report_result

    def get_latest_trend_result(self, task_id: UUID) -> TrendResult | None:
        """查询任务最新趋势分析结果。"""
        statement = select(TrendResult).where(TrendResult.task_id == task_id).order_by(TrendResult.created_at.desc())
        return self.db_session.scalar(statement)

    def get_latest_product_result(self, task_id: UUID) -> ProductResult | None:
        """查询任务最新商品分析结果。"""
        statement = select(ProductResult).where(ProductResult.task_id == task_id).order_by(ProductResult.created_at.desc())
        return self.db_session.scalar(statement)

    def get_latest_review_result(self, task_id: UUID) -> ReviewResult | None:
        """查询任务最新评论分析结果。"""
        statement = select(ReviewResult).where(ReviewResult.task_id == task_id).order_by(ReviewResult.created_at.desc())
        return self.db_session.scalar(statement)

    def get_latest_score_result(self, task_id: UUID) -> ScoreResult | None:
        """查询任务最新评分结果。"""
        statement = select(ScoreResult).where(ScoreResult.task_id == task_id).order_by(ScoreResult.created_at.desc())
        return self.db_session.scalar(statement)

    def get_latest_report(self, task_id: UUID) -> Report | None:
        """查询任务最新报告。"""
        statement = select(Report).where(Report.task_id == task_id).order_by(Report.created_at.desc())
        return self.db_session.scalar(statement)
