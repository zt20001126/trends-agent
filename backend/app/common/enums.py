from enum import StrEnum


class SelectionTaskStatus(StrEnum):
    """选品分析任务状态枚举，约束任务生命周期。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"

