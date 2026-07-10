from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.repositories.selection_repository import SelectionRepository


def test_analyze_selection_api_happy_path() -> None:
    """验证选品分析接口可以完成 MVP 全流程并返回 Markdown 报告。"""
    client = TestClient(app)

    response = client.post("/api/v1/selections/analyze", json={"keyword": "智能手环", "country": "US"})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["status"] in ["completed", "completed_with_warnings"]
    assert len(payload["execution_steps"]) >= 8
    assert payload["execution_steps"][0]["code"] == "create_task_context"
    assert payload["execution_steps"][-1]["code"] == "persist_results"
    assert "智能手环" in payload["report"]
    assert "风险说明" in payload["report"]

    task_id = UUID(payload["task_id"])
    db_session = SessionLocal()
    try:
        repository = SelectionRepository(db_session)
        task = repository.get_task(task_id)
        if task is not None:
            db_session.delete(task)
            db_session.commit()
    finally:
        db_session.close()


def test_get_selection_task_api_returns_not_found() -> None:
    """验证查询不存在任务时返回统一业务错误。"""
    client = TestClient(app)

    response = client.get("/api/v1/selections/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["code"] == "SELECTION_TASK_NOT_FOUND"
