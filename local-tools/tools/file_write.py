"""
文件写入工具
提供安全的文件写入功能
"""

import os
import logging
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from permissions.permission_manager import check_permission, check_path_security

logger = logging.getLogger(__name__)


def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    写入文件内容

    Args:
        args: 包含以下字段的字典
            - path (str): 文件路径，必填
            - content (str): 要写入的内容，必填
            - encoding (str, 可选): 文件编码，默认为 "utf-8"
            - overwrite (bool, 可选): 是否覆盖现有文件，默认为 False
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"path": "写入的文件路径"}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 write:file 权限
        - INVALID_INPUT: 输入参数无效或路径不安全
        - ALREADY_EXISTS: 文件已存在且 overwrite=False
        - IO_ERROR: 文件写入错误
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
        content = args.get("content")
        user_id = args.get("user_id")

        if not path:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: path"
                }
            }

        if content is None:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: content"
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
        if not check_permission(user_id, "write:file"):
            logger.warning(f"用户 {user_id} 尝试写入文件但没有权限: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有文件写入权限"
                }
            }

        # 路径安全检查
        if not check_path_security(path):
            logger.warning(f"用户 {user_id} 尝试写入不安全路径: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "文件路径不安全或指向受保护目录"
                }
            }

        # 获取参数
        encoding = args.get("encoding", "utf-8")
        overwrite = args.get("overwrite", False)

        # 检查文件是否存在
        file_exists = os.path.exists(path)

        if file_exists and not overwrite:
            return {
                "success": False,
                "error": {
                    "error_code": "ALREADY_EXISTS",
                    "message": f"文件已存在且不允许覆盖: {path}"
                }
            }

        # 如果路径包含目录，确保目录存在
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"创建目录: {dir_path}")
            except Exception as e:
                logger.error(f"创建目录失败 {dir_path}: {e}")
                return {
                    "success": False,
                    "error": {
                        "error_code": "IO_ERROR",
                        "message": f"创建目录失败: {str(e)}"
                    }
                }

        # 写入文件内容
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(str(content))

            logger.info(f"用户 {user_id} 成功写入文件: {path}")
            return {
                "success": True,
                "output": {
                    "path": path
                }
            }

        except PermissionError as e:
            logger.error(f"文件权限错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": "文件权限不足，无法写入文件"
                }
            }

        except Exception as e:
            logger.error(f"写入文件时发生未知错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"写入文件时发生错误: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"文件写入工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "IO_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
