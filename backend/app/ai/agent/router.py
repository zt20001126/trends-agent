class SkillRouter:
    """Skill 路由器，当前 MVP 保留路由边界，后续可按任务类型动态选择 Skill。"""

    def route(self, skill_name: str) -> str:
        """返回目标 Skill 名称，作为后续动态路由扩展点。"""
        return skill_name

