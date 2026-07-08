"""create selection analysis tables

Revision ID: 0001_create_selection_analysis_tables
Revises: None
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_selection_analysis_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "selection_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="选品分析任务唯一 ID"),
        sa.Column("keyword", sa.String(length=255), nullable=False, comment="用户输入的原始商品关键词"),
        sa.Column("normalized_keyword", sa.String(length=255), nullable=True, comment="归一化后的英文检索关键词"),
        sa.Column("country", sa.String(length=10), nullable=False, server_default="US", comment="目标站点国家代码"),
        sa.Column("language", sa.String(length=20), nullable=False, server_default="zh-CN", comment="用户输入语言"),
        sa.Column("status", sa.String(length=30), nullable=False, comment="任务状态"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="任务失败或部分失败的错误信息"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="更新时间"),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'completed_with_warnings')", name="ck_selection_tasks_status"),
        comment="选品分析任务主表",
    )

    op.create_table(
        "trend_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="趋势分析结果唯一 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联的选品分析任务 ID"),
        sa.Column("keyword", sa.String(length=255), nullable=False, comment="用于趋势分析的关键词"),
        sa.Column("country", sa.String(length=10), nullable=False, comment="趋势分析国家代码"),
        sa.Column("trend_score", sa.Numeric(5, 2), nullable=True, comment="趋势评分，范围 0 到 100"),
        sa.Column("growth_rate", sa.Numeric(8, 4), nullable=True, comment="趋势增长率"),
        sa.Column("avg_interest", sa.Numeric(5, 2), nullable=True, comment="平均搜索热度"),
        sa.Column("peak_interest", sa.Numeric(5, 2), nullable=True, comment="峰值搜索热度"),
        sa.Column("trend_series", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="趋势时间序列"),
        sa.Column("related_queries", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="相关查询词"),
        sa.Column("data_source", sa.String(length=50), nullable=False, comment="趋势数据来源"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["selection_tasks.id"], ondelete="CASCADE"),
        sa.CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 100)", name="ck_trend_results_trend_score"),
        comment="趋势分析结果表",
    )

    op.create_table(
        "product_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="商品分析结果唯一 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联的选品分析任务 ID"),
        sa.Column("matched_product_count", sa.Integer(), nullable=False, server_default="0", comment="匹配到的商品数量"),
        sa.Column("brand_distribution", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="品牌分布统计"),
        sa.Column("category_distribution", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="类目分布统计"),
        sa.Column("price_min", sa.Numeric(10, 2), nullable=True, comment="最低价格"),
        sa.Column("price_max", sa.Numeric(10, 2), nullable=True, comment="最高价格"),
        sa.Column("price_median", sa.Numeric(10, 2), nullable=True, comment="价格中位数"),
        sa.Column("price_avg", sa.Numeric(10, 2), nullable=True, comment="平均价格"),
        sa.Column("competition_score", sa.Numeric(5, 2), nullable=True, comment="竞争强度评分，范围 0 到 100"),
        sa.Column("sample_products", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="样例商品列表"),
        sa.Column("data_source", sa.String(length=50), nullable=False, comment="商品数据来源"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["selection_tasks.id"], ondelete="CASCADE"),
        sa.CheckConstraint("matched_product_count >= 0", name="ck_product_results_matched_product_count"),
        sa.CheckConstraint("competition_score IS NULL OR (competition_score >= 0 AND competition_score <= 100)", name="ck_product_results_competition_score"),
        comment="商品竞品分析结果表",
    )

    op.create_table(
        "review_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="评论分析结果唯一 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联的选品分析任务 ID"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0", comment="参与分析的评论数量"),
        sa.Column("positive_ratio", sa.Numeric(5, 4), nullable=True, comment="正面评论比例"),
        sa.Column("negative_ratio", sa.Numeric(5, 4), nullable=True, comment="负面评论比例"),
        sa.Column("sentiment_score", sa.Numeric(5, 2), nullable=True, comment="情感评分，范围 0 到 100"),
        sa.Column("pain_points", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="用户痛点列表"),
        sa.Column("improvements", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="产品改进建议列表"),
        sa.Column("representative_reviews", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"), comment="代表性评论列表"),
        sa.Column("data_source", sa.String(length=50), nullable=False, comment="评论数据来源"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["selection_tasks.id"], ondelete="CASCADE"),
        sa.CheckConstraint("review_count >= 0", name="ck_review_results_review_count"),
        sa.CheckConstraint("positive_ratio IS NULL OR (positive_ratio >= 0 AND positive_ratio <= 1)", name="ck_review_results_positive_ratio"),
        sa.CheckConstraint("negative_ratio IS NULL OR (negative_ratio >= 0 AND negative_ratio <= 1)", name="ck_review_results_negative_ratio"),
        sa.CheckConstraint("sentiment_score IS NULL OR (sentiment_score >= 0 AND sentiment_score <= 100)", name="ck_review_results_sentiment_score"),
        comment="评论痛点分析结果表",
    )

    op.create_table(
        "score_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="评分结果唯一 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联的选品分析任务 ID"),
        sa.Column("trend_score", sa.Numeric(5, 2), nullable=True, comment="趋势评分"),
        sa.Column("competition_score", sa.Numeric(5, 2), nullable=True, comment="竞争机会评分"),
        sa.Column("pain_point_score", sa.Numeric(5, 2), nullable=True, comment="痛点机会评分"),
        sa.Column("profit_score", sa.Numeric(5, 2), nullable=True, comment="利润潜力评分"),
        sa.Column("opportunity_score", sa.Numeric(5, 2), nullable=True, comment="综合机会评分"),
        sa.Column("score_detail", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb"), comment="评分明细"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["selection_tasks.id"], ondelete="CASCADE"),
        sa.CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 100)", name="ck_score_results_trend_score"),
        sa.CheckConstraint("competition_score IS NULL OR (competition_score >= 0 AND competition_score <= 100)", name="ck_score_results_competition_score"),
        sa.CheckConstraint("pain_point_score IS NULL OR (pain_point_score >= 0 AND pain_point_score <= 100)", name="ck_score_results_pain_point_score"),
        sa.CheckConstraint("profit_score IS NULL OR (profit_score >= 0 AND profit_score <= 100)", name="ck_score_results_profit_score"),
        sa.CheckConstraint("opportunity_score IS NULL OR (opportunity_score >= 0 AND opportunity_score <= 100)", name="ck_score_results_opportunity_score"),
        comment="选品机会评分结果表",
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, comment="报告唯一 ID"),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False, comment="关联的选品分析任务 ID"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="报告标题"),
        sa.Column("markdown_content", sa.Text(), nullable=False, comment="Markdown 格式报告正文"),
        sa.Column("summary", sa.Text(), nullable=True, comment="报告摘要"),
        sa.Column("recommendation", sa.String(length=50), nullable=True, comment="开发建议枚举值"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.ForeignKeyConstraint(["task_id"], ["selection_tasks.id"], ondelete="CASCADE"),
        comment="选品分析报告表",
    )

    op.create_index("idx_selection_tasks_keyword", "selection_tasks", ["keyword"])
    op.create_index("idx_selection_tasks_status", "selection_tasks", ["status"])
    op.create_index("idx_selection_tasks_created_at", "selection_tasks", ["created_at"])
    op.create_index("idx_trend_results_task_id", "trend_results", ["task_id"])
    op.create_index("idx_product_results_task_id", "product_results", ["task_id"])
    op.create_index("idx_review_results_task_id", "review_results", ["task_id"])
    op.create_index("idx_score_results_task_id", "score_results", ["task_id"])
    op.create_index("idx_reports_task_id", "reports", ["task_id"])


def downgrade() -> None:
    op.drop_index("idx_reports_task_id", table_name="reports")
    op.drop_index("idx_score_results_task_id", table_name="score_results")
    op.drop_index("idx_review_results_task_id", table_name="review_results")
    op.drop_index("idx_product_results_task_id", table_name="product_results")
    op.drop_index("idx_trend_results_task_id", table_name="trend_results")
    op.drop_index("idx_selection_tasks_created_at", table_name="selection_tasks")
    op.drop_index("idx_selection_tasks_status", table_name="selection_tasks")
    op.drop_index("idx_selection_tasks_keyword", table_name="selection_tasks")
    op.drop_table("reports")
    op.drop_table("score_results")
    op.drop_table("review_results")
    op.drop_table("product_results")
    op.drop_table("trend_results")
    op.drop_table("selection_tasks")

