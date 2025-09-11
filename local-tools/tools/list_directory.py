"""
目录列举工具
提供安全的目录内容列举功能
"""

import os
import stat
import logging
from datetime import datetime
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from permissions.permission_manager import check_permission, check_path_security

logger = logging.getLogger(__name__)


def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    列举目录内容

    Args:
        args: 包含以下字段的字典
            - path (str): 目录路径，必填
            - include_hidden (bool, 可选): 是否包含隐藏文件，默认为 False
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"entries": [...]}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 read:file 权限
        - INVALID_INPUT: 输入参数无效或路径不安全
        - NOT_FOUND: 目录不存在
        - IO_ERROR: 读取目录失败
    """
    try:
        # 参数验证
        if not isinstance(args, dict):
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "输入参数必须是字典类型"
                }
            }

        # 提取必需参数
        path = args.get("path")
        user_id = args.get("user_id")

        if not path:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: path"
                }
            }

        if not user_id:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: user_id"
                }
            }

        # 权限检查
        if not check_permission(user_id, "read:file"):
            logger.warning(f"用户 {user_id} 尝试列举目录但没有权限: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有文件读取权限"
                }
            }

        # 路径安全检查
        if not check_path_security(path):
            logger.warning(f"用户 {user_id} 尝试列举不安全路径: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "目录路径不安全或指向受保护目录"
                }
            }

        # 获取参数
        include_hidden = args.get("include_hidden", False)

        # 检查目录是否存在
        if not os.path.exists(path):
            return {
                "success": False,
                "error": {
                    "error_code": "NOT_FOUND",
                    "message": f"目录不存在: {path}"
                }
            }

        # 检查是否是目录
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": f"路径不是目录: {path}"
                }
            }

        # 列举目录内容
        try:
            entries = []
            for item in os.listdir(path):
                # 检查是否包含隐藏文件
                if not include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(path, item)

                try:
                    # 获取文件状态
                    stat_info = os.stat(item_path)

                    # 确定文件类型
                    if os.path.isdir(item_path):
                        item_type = "directory"
                    elif os.path.isfile(item_path):
                        item_type = "file"
                    else:
                        item_type = "other"

                    # 格式化修改时间
                    modified_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()

                    entries.append({
                        "name": item,
                        "type": item_type,
                        "size": stat_info.st_size,
                        "last_modified": modified_time
                    })

                except (OSError, PermissionError) as e:
                    logger.warning(f"无法获取文件信息 {item_path}: {e}")
                    # 仍然添加条目，但使用默认值
                    entries.append({
                        "name": item,
                        "type": "unknown",
                        "size": 0,
                        "last_modified": ""
                    })

            # 按名称排序
            entries.sort(key=lambda x: x["name"].lower())

            logger.info(f"用户 {user_id} 成功列举目录: {path}，共 {len(entries)} 项")
            return {
                "success": True,
                "output": {
                    "entries": entries
                }
            }

        except PermissionError as e:
            logger.error(f"目录权限错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": "目录权限不足，无法读取目录内容"
                }
            }

        except Exception as e:
            logger.error(f"列举目录时发生未知错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"读取目录时发生错误: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"目录列举工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "IO_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
