from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def selection_frontend() -> HTMLResponse:
    """返回 MVP 前端页面，用于本地展示和手动触发选品分析。"""
    html_path = Path(__file__).resolve().parents[3] / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

