"""
权限管理器
提供用户权限检查功能
"""

import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)


class PermissionManager:
    """
    权限管理器类
    管理用户权限和权限检查
    """

    def __init__(self):
        # 权限映射：user_id -> set of permissions
        self._user_permissions: Dict[str, Set[str]] = {}

        # 默认权限列表
        self._default_permissions = {
            "admin": {
                "read:file",
                "write:file",
                "delete:file",
                "execute:command",
                "network:outbound"
            },
            "user": {
                "read:file",
                "write:file",
                "execute:command"
            },
            "readonly": {
                "read:file"
            }
        }

        # 系统受保护路径
        self._protected_paths = {
            "/etc",
            "/usr",
            "/bin",
            "/sbin",
            "/System",  # macOS
            "/Windows",  # Windows
            "/Program Files",
            "/Program Files (x86)"
        }

        # 初始化默认用户权限
        self._initialize_default_permissions()

    def _initialize_default_permissions(self):
        """初始化默认用户权限"""
        for user_id, permissions in self._default_permissions.items():
            self._user_permissions[user_id] = permissions.copy()

    def add_user_permission(self, user_id: str, permission: str) -> None:
        """
        为用户添加权限

        Args:
            user_id: 用户ID
            permission: 权限字符串
        """
        if user_id not in self._user_permissions:
            self._user_permissions[user_id] = set()

        self._user_permissions[user_id].add(permission)
        logger.info(f"为用户 {user_id} 添加权限: {permission}")

    def remove_user_permission(self, user_id: str, permission: str) -> None:
        """
        从用户移除权限

        Args:
            user_id: 用户ID
            permission: 权限字符串
        """
        if user_id in self._user_permissions:
            self._user_permissions[user_id].discard(permission)
            logger.info(f"从用户 {user_id} 移除权限: {permission}")

    def set_user_permissions(self, user_id: str, permissions: Set[str]) -> None:
        """
        设置用户的完整权限集

        Args:
            user_id: 用户ID
            permissions: 权限集合
        """
        self._user_permissions[user_id] = permissions.copy()
        logger.info(f"为用户 {user_id} 设置权限: {permissions}")

    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        检查用户是否有指定权限

        Args:
            user_id: 用户ID
            permission: 权限字符串

        Returns:
            bool: True 如果用户有权限，否则 False
        """
        if user_id not in self._user_permissions:
            logger.warning(f"用户 {user_id} 未找到权限记录")
            return False

        has_permission = permission in self._user_permissions[user_id]
        logger.debug(f"用户 {user_id} 权限检查 {permission}: {has_permission}")
        return has_permission

    def check_path_security(self, path: str) -> bool:
        """
        检查路径是否安全（不指向系统受保护目录）

        Args:
            path: 文件路径

        Returns:
            bool: True 如果路径安全，否则 False
        """
        import os

        # 获取绝对路径
        abs_path = os.path.abspath(path)

        # 检查是否指向受保护路径
        for protected_path in self._protected_paths:
            if abs_path.startswith(protected_path):
                logger.warning(f"路径 {path} 指向受保护目录 {protected_path}")
                return False

        return True

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """
        获取用户的权限列表

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 用户权限集合
        """
        return self._user_permissions.get(user_id, set()).copy()


# 全局权限管理器实例
_permission_manager = None


def get_permission_manager() -> PermissionManager:
    """获取全局权限管理器实例"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


def check_permission(user_id: str, permission: str) -> bool:
    """
    检查用户权限的便捷函数

    Args:
        user_id: 用户ID
        permission: 权限字符串

    Returns:
        bool: True 如果用户有权限，否则 False
    """
    return get_permission_manager().check_permission(user_id, permission)


def check_path_security(path: str) -> bool:
    """
    检查路径安全的便捷函数

    Args:
        path: 文件路径

    Returns:
        bool: True 如果路径安全，否则 False
    """
    return get_permission_manager().check_path_security(path)
