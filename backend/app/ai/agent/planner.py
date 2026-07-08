class SelectionPlanner:
    """选品 Agent 任务规划器，当前 MVP 使用固定可控步骤。"""

    def plan(self) -> list[str]:
        """返回固定分析步骤，后续可扩展为基于任务类型的动态规划。"""
        return ["trend", "product", "review", "scoring", "report"]

