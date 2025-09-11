"""
Fei 角色实现
数据库专家 - 负责数据存储和数据库设计
"""

from .base_role import Role


class Fei(Role):
    """Fei - 数据库专家"""

    def _get_system_prompt(self) -> str:
        return """# Fei - 数据库专家

你是一个数据库设计和优化专家，专注于数据存储解决方案。"""

    def act(self, context):
        return super().act(context)

    def get_capabilities(self):
        return ["数据库设计", "性能优化", "数据建模", "SQL优化"]
