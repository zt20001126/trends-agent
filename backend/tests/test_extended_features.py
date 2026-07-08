from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.providers.commercial import AmazonSpApiProvider, KeepaProvider, SellerSpriteProvider
from app.repositories.selection_repository import SelectionRepository
from app.tools.product_analysis import ProductAnalysisTool


def test_product_analysis_tool_has_streaming_interface() -> None:
    """验证商品分析 Tool 预留 streaming 数据读取接口。"""
    result = ProductAnalysisTool().analyze_streaming(keyword="smart fitness band")

    assert result.data_source == "huggingface_streaming_not_configured"


def test_commercial_provider_interfaces_are_defined() -> None:
    """验证商业数据源 Provider 边界已定义。"""
    assert KeepaProvider().provider_name == "keepa"
    assert AmazonSpApiProvider().provider_name == "amazon_sp_api"
    assert SellerSpriteProvider().provider_name == "seller_sprite"


def test_selection_history_batch_async_and_frontend_endpoints() -> None:
    """验证历史列表、批量分析、异步分析和前端页面接口。"""
    client = TestClient(app)
    created_task_ids: list[UUID] = []

    batch_response = client.post(
        "/api/v1/selections/batch-analyze",
        json={"keywords": ["portable blender", "dog water bottle"], "country": "US"},
    )
    assert batch_response.status_code == 200
    batch_results = batch_response.json()["data"]["results"]
    assert len(batch_results) == 2
    created_task_ids.extend(UUID(item["task_id"]) for item in batch_results)

    async_response = client.post("/api/v1/selections/analyze-async", json={"keyword": "智能手环", "country": "US"})
    assert async_response.status_code == 200
    async_task_id = UUID(async_response.json()["data"]["task_id"])
    created_task_ids.append(async_task_id)

    detail_response = client.get(f"/api/v1/selections/{async_task_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["task"]["status"] in ["completed", "completed_with_warnings"]

    list_response = client.get("/api/v1/selections?limit=10&offset=0")
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["items"]) >= 1

    frontend_response = client.get("/api/v1/")
    assert frontend_response.status_code == 200
    assert "AI跨境电商选品智能体" in frontend_response.text

    db_session = SessionLocal()
    try:
        repository = SelectionRepository(db_session)
        for task_id in created_task_ids:
            task = repository.get_task(task_id)
            if task is not None:
                db_session.delete(task)
        db_session.commit()
    finally:
        db_session.close()

