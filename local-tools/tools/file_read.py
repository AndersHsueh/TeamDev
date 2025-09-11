"""
文件读取工具
提供安全的文件读取功能
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
    读取文件内容

    Args:
        args: 包含以下字段的字典
            - path (str): 文件路径，必填
            - encoding (str, 可选): 文件编码，默认为 "utf-8"
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"content": "文件内容"}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 read:file 权限
        - INVALID_INPUT: 输入参数无效或路径不安全
        - NOT_FOUND: 文件不存在
        - IO_ERROR: 文件读取错误
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
            logger.warning(f"用户 {user_id} 尝试读取文件但没有权限: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有文件读取权限"
                }
            }

        # 路径安全检查
        if not check_path_security(path):
            logger.warning(f"用户 {user_id} 尝试读取不安全路径: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "文件路径不安全或指向受保护目录"
                }
            }

        # 获取编码参数
        encoding = args.get("encoding", "utf-8")

        # 检查文件是否存在
        if not os.path.exists(path):
            return {
                "success": False,
                "error": {
                    "error_code": "NOT_FOUND",
                    "message": f"文件不存在: {path}"
                }
            }

        # 检查是否是文件
        if not os.path.isfile(path):
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": f"路径不是文件: {path}"
                }
            }

        # 读取文件内容
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            logger.info(f"用户 {user_id} 成功读取文件: {path}")
            return {
                "success": True,
                "output": {
                    "content": content
                }
            }

        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"文件编码错误，无法以 {encoding} 编码读取文件"
                }
            }

        except PermissionError as e:
            logger.error(f"文件权限错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": "文件权限不足，无法读取文件"
                }
            }

        except Exception as e:
            logger.error(f"读取文件时发生未知错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"读取文件时发生错误: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"文件读取工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "IO_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
