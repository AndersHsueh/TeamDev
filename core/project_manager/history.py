"""
历史记录管理
管理文档的历史版本和回滚功能
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import difflib

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    历史记录管理器

    负责文档的历史版本管理和回滚功能
    """

    def __init__(self, history_dir: str = "./history"):
        """
        初始化历史管理器

        Args:
            history_dir: 历史记录目录
        """
        self.history_dir = os.path.abspath(history_dir)
        os.makedirs(self.history_dir, exist_ok=True)

    def save_version(self, file_path: str, content: str,
                    user_id: str, message: str = "") -> str:
        """
        保存文件版本

        Args:
            file_path: 原始文件路径
            content: 文件内容
            user_id: 用户ID
            message: 版本说明

        Returns:
            str: 版本ID
        """
        try:
            # 生成版本ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            version_id = f"{timestamp}_{user_id}"

            # 创建版本目录
            version_dir = os.path.join(self.history_dir, version_id)
            os.makedirs(version_dir, exist_ok=True)

            # 保存文件内容
            content_file = os.path.join(version_dir, filename)
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 保存元信息
            meta = {
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "file_path": file_path,
                "file_size": len(content),
                "message": message or f"自动保存版本 {version_id}"
            }

            meta_file = os.path.join(version_dir, "meta.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            logger.info(f"版本保存成功: {version_id} - {file_path}")
            return version_id

        except Exception as e:
            logger.error(f"保存版本失败: {e}")
            return ""

    def get_versions(self, file_path: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取版本历史

        Args:
            file_path: 指定文件路径，如果为None则返回所有版本
            limit: 返回的最大版本数量

        Returns:
            List[Dict[str, Any]]: 版本列表
        """
        versions = []

        try:
            if os.path.exists(self.history_dir):
                for item in sorted(os.listdir(self.history_dir), reverse=True):
                    version_dir = os.path.join(self.history_dir, item)
                    if os.path.isdir(version_dir):
                        meta_file = os.path.join(version_dir, "meta.json")
                        if os.path.exists(meta_file):
                            with open(meta_file, 'r', encoding='utf-8') as f:
                                meta = json.load(f)

                            # 过滤指定文件
                            if file_path and meta.get("file_path") != file_path:
                                continue

                            versions.append(meta)

                            if len(versions) >= limit:
                                break

        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")

        return versions

    def rollback_to_version(self, version_id: str, target_path: str) -> bool:
        """
        回滚到指定版本

        Args:
            version_id: 版本ID
            target_path: 目标文件路径

        Returns:
            bool: 回滚是否成功
        """
        try:
            version_dir = os.path.join(self.history_dir, version_id)
            if not os.path.exists(version_dir):
                logger.warning(f"版本不存在: {version_id}")
                return False

            # 查找版本文件
            meta_file = os.path.join(version_dir, "meta.json")
            if not os.path.exists(meta_file):
                logger.warning(f"版本元信息不存在: {version_id}")
                return False

            # 获取原始文件名
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            original_filename = os.path.basename(meta["file_path"])
            content_file = os.path.join(version_dir, original_filename)

            if not os.path.exists(content_file):
                logger.warning(f"版本文件不存在: {content_file}")
                return False

            # 读取内容并写入目标文件
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"成功回滚到版本: {version_id} -> {target_path}")
            return True

        except Exception as e:
            logger.error(f"回滚版本失败: {e}")
            return False

    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        比较两个版本的差异

        Args:
            version_id1: 版本ID 1
            version_id2: 版本ID 2

        Returns:
            Dict[str, Any]: 比较结果
        """
        try:
            # 获取两个版本的内容
            content1 = self._get_version_content(version_id1)
            content2 = self._get_version_content(version_id2)

            if content1 is None or content2 is None:
                return {"error": "无法获取版本内容"}

            # 生成差异
            diff = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"version_{version_id1}",
                tofile=f"version_{version_id2}",
                lineterm=""
            ))

            return {
                "version1": version_id1,
                "version2": version_id2,
                "diff": "".join(diff),
                "has_changes": len(diff) > 0
            }

        except Exception as e:
            logger.error(f"比较版本失败: {e}")
            return {"error": str(e)}

    def _get_version_content(self, version_id: str) -> Optional[str]:
        """
        获取版本文件内容

        Args:
            version_id: 版本ID

        Returns:
            Optional[str]: 文件内容
        """
        try:
            version_dir = os.path.join(self.history_dir, version_id)
            meta_file = os.path.join(version_dir, "meta.json")

            if not os.path.exists(meta_file):
                return None

            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            filename = os.path.basename(meta["file_path"])
            content_file = os.path.join(version_dir, filename)

            if not os.path.exists(content_file):
                return None

            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"获取版本内容失败 {version_id}: {e}")
            return None


# 全局历史管理器实例
_history_manager = None


def get_history_manager() -> HistoryManager:
    """获取全局历史管理器实例"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager
