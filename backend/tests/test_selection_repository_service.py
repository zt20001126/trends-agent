from uuid import uuid4

import pytest

from app.common.exceptions import BusinessException
from app.db.session import SessionLocal
from app.repositories.selection_repository import SelectionRepository
from app.schemas.selection import SelectionAnalyzeRequest
from app.services.selection_service import SelectionService


def test_selection_service_creates_and_reads_task_detail() -> None:
    """验证 Service 可以创建任务并聚合任务详情。"""
    db_session = SessionLocal()
    try:
        service = SelectionService(db_session)
        request = SelectionAnalyzeRequest(keyword="智能手环", country="US", language="zh-CN")

        task = service.create_task(request)
        db_session.commit()

        detail = service.get_task_detail(task.id)

        assert detail.task.id == task.id
        assert detail.task.keyword == "智能手环"
        assert detail.task.country == "US"
        assert detail.trend_result is None
    finally:
        repository = SelectionRepository(db_session)
        persisted_task = repository.get_task(task.id) if "task" in locals() else None
        if persisted_task is not None:
            db_session.delete(persisted_task)
            db_session.commit()
        db_session.close()


def test_selection_service_raises_when_task_not_found() -> None:
    """验证查询不存在任务时返回业务异常。"""
    db_session = SessionLocal()
    try:
        service = SelectionService(db_session)

        with pytest.raises(BusinessException) as exception_info:
            service.get_task_detail(uuid4())

        assert exception_info.value.code == "SELECTION_TASK_NOT_FOUND"
    finally:
        db_session.close()

