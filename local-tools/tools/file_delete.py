"""
文件删除工具
提供安全的文件和目录删除功能
"""

import os
import shutil
import logging
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from permissions.permission_manager import check_permission, check_path_security

logger = logging.getLogger(__name__)


def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    删除文件或目录

    Args:
        args: 包含以下字段的字典
            - path (str): 文件或目录路径，必填
            - recursive (bool, 可选): 是否递归删除目录，默认为 False
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"path": "删除的路径"}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 delete:file 权限
        - INVALID_INPUT: 输入参数无效或路径不安全
        - NOT_FOUND: 文件或目录不存在
        - IO_ERROR: 删除操作失败
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
        if not check_permission(user_id, "delete:file"):
            logger.warning(f"用户 {user_id} 尝试删除文件但没有权限: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有文件删除权限"
                }
            }

        # 路径安全检查
        if not check_path_security(path):
            logger.warning(f"用户 {user_id} 尝试删除不安全路径: {path}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "文件路径不安全或指向受保护目录"
                }
            }

        # 获取参数
        recursive = args.get("recursive", False)

        # 检查路径是否存在
        if not os.path.exists(path):
            return {
                "success": False,
                "error": {
                    "error_code": "NOT_FOUND",
                    "message": f"路径不存在: {path}"
                }
            }

        # 执行删除操作
        try:
            if os.path.isfile(path):
                # 删除文件
                os.remove(path)
                logger.info(f"用户 {user_id} 成功删除文件: {path}")

            elif os.path.isdir(path):
                # 删除目录
                if recursive:
                    shutil.rmtree(path)
                    logger.info(f"用户 {user_id} 成功递归删除目录: {path}")
                else:
                    # 检查目录是否为空
                    if os.listdir(path):
                        return {
                            "success": False,
                            "error": {
                                "error_code": "IO_ERROR",
                                "message": "目录不为空且未设置递归删除"
                            }
                        }
                    os.rmdir(path)
                    logger.info(f"用户 {user_id} 成功删除空目录: {path}")
            else:
                return {
                    "success": False,
                    "error": {
                        "error_code": "INVALID_INPUT",
                        "message": f"路径既不是文件也不是目录: {path}"
                    }
                }

            return {
                "success": True,
                "output": {
                    "path": path
                }
            }

        except PermissionError as e:
            logger.error(f"删除权限错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": "权限不足，无法删除文件或目录"
                }
            }

        except OSError as e:
            logger.error(f"删除操作失败 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"删除操作失败: {str(e)}"
                }
            }

        except Exception as e:
            logger.error(f"删除时发生未知错误 {path}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "IO_ERROR",
                    "message": f"删除时发生错误: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"文件删除工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "IO_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
