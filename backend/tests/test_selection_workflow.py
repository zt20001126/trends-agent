from app.ai.workflow.selection_graph import SelectionWorkflow
from app.db.session import SessionLocal
from app.repositories.selection_repository import SelectionRepository
from app.skills.trend.skill import TrendSkill
from app.tools.google_trend import GoogleTrendTool


def test_selection_workflow_happy_path_persists_results() -> None:
    """验证 LangGraph 工作流可以完成分析并持久化结果。"""
    db_session = SessionLocal()
    try:
        repository = SelectionRepository(db_session)
        task = repository.create_task(keyword="智能手环", country="US", language="zh-CN", status="running")
        workflow = SelectionWorkflow(trend_skill=TrendSkill(GoogleTrendTool(enable_live=False)))

        final_state = workflow.run(
            task_id=task.id,
            keyword=task.keyword,
            country=task.country,
            language=task.language,
            repository=repository,
        )
        db_session.commit()

        persisted_task = repository.get_task(task.id)
        report = repository.get_latest_report(task.id)

        assert final_state["normalized_keyword"]
        assert len(final_state["execution_steps"]) >= 8
        assert final_state["execution_steps"][3]["code"] == "run_trend_skill"
        assert persisted_task is not None
        assert persisted_task.status in ["completed", "completed_with_warnings"]
        assert report is not None
        assert "智能手环" in report.markdown_content
        assert "风险说明" in report.markdown_content
    finally:
        persisted_task = repository.get_task(task.id) if "task" in locals() else None
        if persisted_task is not None:
            db_session.delete(persisted_task)
            db_session.commit()
        db_session.close()
