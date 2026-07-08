from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db_session


def get_database_session() -> Generator[Session, None, None]:
    """数据库会话依赖，统一对 API route 暴露 session 获取方式。"""
    yield from get_db_session()

