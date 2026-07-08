"""SQLAlchemy 持久化模型包。"""

from app.models.product_result import ProductResult
from app.models.report import Report
from app.models.review_result import ReviewResult
from app.models.score_result import ScoreResult
from app.models.selection_task import SelectionTask
from app.models.trend_result import TrendResult

__all__ = [
    "ProductResult",
    "Report",
    "ReviewResult",
    "ScoreResult",
    "SelectionTask",
    "TrendResult",
]
