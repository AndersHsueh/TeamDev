"""
Peipei 角色实现
测试员 - 负责质量保证和测试
"""

from .base_role import Role


class Peipei(Role):
    """Peipei - 测试专家"""

    def _get_system_prompt(self) -> str:
        return """# Peipei - 测试专家

你是一个质量保证和测试专家，专注于软件测试和质量控制。"""

    def act(self, context):
        return super().act(context)

    def get_capabilities(self):
        return ["测试策略", "自动化测试", "质量保证", "缺陷管理"]
