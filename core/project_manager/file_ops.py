"""
文件操作模块
提供安全的文件读写和备份功能
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FileOperations:
    """
    文件操作类

    提供安全的文件操作功能，包括自动备份
    """

    def __init__(self, backup_dir: str = "./backups"):
        """
        初始化文件操作器

        Args:
            backup_dir: 备份目录
        """
        self.backup_dir = os.path.abspath(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_with_backup(self, file_path: str, content: str,
                        user_id: str = "system") -> bool:
        """
        保存文件并自动备份

        Args:
            file_path: 文件路径
            content: 文件内容
            user_id: 用户ID

        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 如果文件存在，先备份
            if os.path.exists(file_path):
                self._create_backup(file_path, user_id)

            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"文件保存成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存文件失败 {file_path}: {e}")
            return False

    def read_file(self, file_path: str) -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 文件内容，如果读取失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None

    def _create_backup(self, file_path: str, user_id: str):
        """
        创建文件备份

        Args:
            file_path: 要备份的文件路径
            user_id: 用户ID
        """
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{os.path.splitext(filename)[0]}_{user_id}_{timestamp}{os.path.splitext(filename)[1]}"
            backup_path = os.path.join(self.backup_dir, backup_name)

            # 复制文件
            shutil.copy2(file_path, backup_path)

            logger.debug(f"备份创建: {backup_path}")

        except Exception as e:
            logger.warning(f"创建备份失败: {e}")


# 全局文件操作器实例
_file_ops = None


def get_file_operations() -> FileOperations:
    """获取全局文件操作器实例"""
    global _file_ops
    if _file_ops is None:
        _file_ops = FileOperations()
    return _file_ops
