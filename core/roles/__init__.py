"""
角色系统模块
提供各种 AI 角色的实现
"""

from .base_role import Role, RoleContext, RoleAction
from .jim import Jim
from .jacky import Jacky
from .happen import Happen
from .fei import Fei
from .peipei import Peipei

__all__ = [
    "Role",
    "RoleContext",
    "RoleAction",
    "Jim",
    "Jacky",
    "Happen",
    "Fei",
    "Peipei"
]


