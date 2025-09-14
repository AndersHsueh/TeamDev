"""
角色系统模块
提供各种AI角色的实现和管理
"""

from .base_role import Role, RoleContext, RoleAction
from .monica import Monica
from .jacky import Jacky
from .happen import Happen
from .fei import Fei
from .peipei import Peipei

__all__ = [
    "Role",
    "RoleContext", 
    "RoleAction",
    "Monica",
    "Jacky",
    "Happen",
    "Fei",
    "Peipei"
]


