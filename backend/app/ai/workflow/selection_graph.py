from typing import Any
from uuid import UUID

from langgraph.graph import END, START, StateGraph

from app.ai.clients.deepseek_client import DeepSeekClient
from app.ai.schemas import SelectionReportInput
from app.ai.workflow.state import SelectionState
from app.common.enums import SelectionTaskStatus
from app.common.exceptions import BusinessException
from app.repositories.selection_repository import SelectionRepository
from app.skills.product.skill import ProductSkill
from app.skills.report.skill import ReportSkill
from app.skills.review.skill import ReviewSkill
from app.skills.scoring.skill import ScoringSkill
from app.skills.trend.skill import TrendSkill


class SelectionWorkflow:
    """LangGraph 选品分析工作流，负责编排 Skill 调用和结果持久化。"""

    FALLBACK_KEYWORDS = {
        "智能手环": "smart fitness band",
    }

    def __init__(
        self,
        deepseek_client: DeepSeekClient | None = None,
        trend_skill: TrendSkill | None = None,
        product_skill: ProductSkill | None = None,
        review_skill: ReviewSkill | None = None,
        scoring_skill: ScoringSkill | None = None,
        report_skill: ReportSkill | None = None,
    ) -> None:
        self.deepseek_client = deepseek_client or DeepSeekClient()
        self.trend_skill = trend_skill or TrendSkill()
        self.product_skill = product_skill or ProductSkill()
        self.review_skill = review_skill or ReviewSkill()
        self.scoring_skill = scoring_skill or ScoringSkill()
        self.report_skill = report_skill or ReportSkill()
        self.graph = self._build_graph()

    def run(
        self,
        task_id: UUID,
        keyword: str,
        country: str,
        language: str,
        repository: SelectionRepository,
    ) -> SelectionState:
        """执行选品分析工作流并返回最终状态。"""
        initial_state: SelectionState = {
            "task_id": task_id,
            "keyword": keyword,
            "country": country,
            "language": language,
            "repository": repository,
            "errors": [],
        }
        return self.graph.invoke(initial_state)

    def _build_graph(self) -> Any:
        """构建 LangGraph 节点和顺序边。"""
        workflow = StateGraph(SelectionState)
        workflow.add_node("create_task_context", self._create_task_context)
        workflow.add_node("normalize_keyword", self._normalize_keyword)
        workflow.add_node("plan_analysis", self._plan_analysis)
        workflow.add_node("run_trend_skill", self._run_trend_skill)
        workflow.add_node("run_product_skill", self._run_product_skill)
        workflow.add_node("run_review_skill", self._run_review_skill)
        workflow.add_node("run_scoring_skill", self._run_scoring_skill)
        workflow.add_node("run_report_skill", self._run_report_skill)
        workflow.add_node("persist_results", self._persist_results)

        workflow.add_edge(START, "create_task_context")
        workflow.add_edge("create_task_context", "normalize_keyword")
        workflow.add_edge("normalize_keyword", "plan_analysis")
        workflow.add_edge("plan_analysis", "run_trend_skill")
        workflow.add_edge("run_trend_skill", "run_product_skill")
        workflow.add_edge("run_product_skill", "run_review_skill")
        workflow.add_edge("run_review_skill", "run_scoring_skill")
        workflow.add_edge("run_scoring_skill", "run_report_skill")
        workflow.add_edge("run_report_skill", "persist_results")
        workflow.add_edge("persist_results", END)
        return workflow.compile()

    def _create_task_context(self, state: SelectionState) -> SelectionState:
        """节点输入：任务基础信息；节点输出：初始化错误列表；下一节点：normalize_keyword。"""
        state.setdefault("errors", [])
        return state

    def _normalize_keyword(self, state: SelectionState) -> SelectionState:
        """节点输入：原始关键词；节点输出：归一化英文关键词；下一节点：plan_analysis。"""
        try:
            result = self.deepseek_client.normalize_keyword(
                keyword=state["keyword"],
                country=state["country"],
                language=state["language"],
            )
            state["normalized_keyword"] = result.normalized_keyword
        except BusinessException as exc:
            # DeepSeek 未配置或调用失败时，使用保守 fallback，保证本地 MVP 可运行。
            state["normalized_keyword"] = self.FALLBACK_KEYWORDS.get(state["keyword"], state["keyword"])
            state["errors"].append({"node": "normalize_keyword", "code": exc.code, "message": exc.message})
        return state

    def _plan_analysis(self, state: SelectionState) -> SelectionState:
        """节点输入：归一化关键词；节点输出：固定分析步骤；下一节点：run_trend_skill。"""
        state["planned_steps"] = [
            "trend",
            "product",
            "review",
            "scoring",
            "report",
        ]
        return state

    def _run_trend_skill(self, state: SelectionState) -> SelectionState:
        """节点输入：归一化关键词；节点输出：趋势分析结果；下一节点：run_product_skill。"""
        state["trend_result"] = self.trend_skill.analyze(
            keyword=state["normalized_keyword"],
            country=state["country"],
        )
        return state

    def _run_product_skill(self, state: SelectionState) -> SelectionState:
        """节点输入：归一化关键词；节点输出：商品分析结果；下一节点：run_review_skill。"""
        state["product_result"] = self.product_skill.analyze(keyword=state["normalized_keyword"])
        return state

    def _run_review_skill(self, state: SelectionState) -> SelectionState:
        """节点输入：归一化关键词；节点输出：评论分析结果；下一节点：run_scoring_skill。"""
        product_ids = [
            str(product.get("parent_asin"))
            for product in state["product_result"].sample_products
            if product.get("parent_asin")
        ]
        state["review_result"] = self.review_skill.analyze(
            keyword=state["normalized_keyword"],
            product_ids=product_ids,
        )
        return state

    def _run_scoring_skill(self, state: SelectionState) -> SelectionState:
        """节点输入：趋势/商品/评论结果；节点输出：机会评分；下一节点：run_report_skill。"""
        state["score_result"] = self.scoring_skill.calculate(
            trend_result=state["trend_result"],
            product_result=state["product_result"],
            review_result=state["review_result"],
        )
        return state

    def _run_report_skill(self, state: SelectionState) -> SelectionState:
        """节点输入：所有分析结果；节点输出：Markdown 报告；下一节点：persist_results。"""
        report_input = SelectionReportInput(
            keyword=state["keyword"],
            normalized_keyword=state["normalized_keyword"],
            country=state["country"],
            trend_result=state["trend_result"].model_dump(mode="json"),
            product_result=state["product_result"].model_dump(mode="json"),
            review_result=state["review_result"].model_dump(mode="json"),
            score_result=state["score_result"].model_dump(mode="json"),
        )
        state["report"] = self.report_skill.generate(report_input)
        return state

    def _persist_results(self, state: SelectionState) -> SelectionState:
        """节点输入：分析 DTO；节点输出：已持久化状态；下一节点：END。"""
        repository = state["repository"]
        task = repository.get_task(state["task_id"])
        if task is None:
            raise BusinessException(message="选品分析任务不存在", code="SELECTION_TASK_NOT_FOUND", http_status=404)

        repository.save_trend_result(state["task_id"], state["trend_result"])
        repository.save_product_result(state["task_id"], state["product_result"])
        repository.save_review_result(state["task_id"], state["review_result"])
        repository.save_score_result(state["task_id"], state["score_result"])
        repository.save_report(state["task_id"], state["report"])

        final_status = (
            SelectionTaskStatus.COMPLETED_WITH_WARNINGS.value
            if state.get("errors")
            else SelectionTaskStatus.COMPLETED.value
        )
        repository.update_task_status(
            task=task,
            status=final_status,
            error_message=str(state.get("errors")) if state.get("errors") else None,
            normalized_keyword=state["normalized_keyword"],
        )
        return state

