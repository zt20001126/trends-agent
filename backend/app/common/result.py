from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """统一 API 响应结构，用于包裹业务接口返回数据。"""

    code: str = Field(default="SUCCESS", description="业务响应码")
    message: str = Field(default="success", description="业务响应消息")
    data: DataT | None = Field(default=None, description="业务响应数据")

