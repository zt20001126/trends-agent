from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok() -> None:
    """验证健康检查接口可以返回系统可用状态。"""
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}

