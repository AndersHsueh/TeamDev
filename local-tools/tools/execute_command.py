"""
命令执行工具
提供安全的系统命令执行功能
"""

import subprocess
import threading
import logging
import shlex
from typing import Dict, Any, Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from permissions.permission_manager import check_permission, check_path_security

logger = logging.getLogger(__name__)


class CommandTimeoutError(Exception):
    """命令执行超时异常"""
    pass


def _run_command_with_timeout(cmd: str, cwd: Optional[str] = None,
                            env: Optional[Dict[str, str]] = None,
                            timeout: int = 60) -> Dict[str, Any]:
    """
    使用超时机制执行命令

    Args:
        cmd: 命令字符串
        cwd: 当前工作目录
        env: 环境变量
        timeout: 超时时间（秒）

    Returns:
        Dict: 包含 stdout, stderr, exit_code 的字典

    Raises:
        CommandTimeoutError: 命令执行超时
    """
    result = {"stdout": "", "stderr": "", "exit_code": -1}

    def target():
        try:
            # 使用 shlex.split 安全地分割命令
            cmd_list = shlex.split(cmd)

            # 执行命令
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env,
                text=True
            )

            stdout, stderr = process.communicate()
            result["stdout"] = stdout or ""
            result["stderr"] = stderr or ""
            result["exit_code"] = process.returncode

        except Exception as e:
            result["stderr"] = str(e)
            result["exit_code"] = -1

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # 超时了，尝试终止进程
        try:
            # 注意：这里无法直接终止子进程，因为我们不知道进程ID
            # 在生产环境中，应该使用更复杂的进程管理机制
            pass
        except:
            pass
        raise CommandTimeoutError(f"命令执行超时 ({timeout}秒)")

    return result


def _is_command_safe(cmd: str) -> bool:
    """
    检查命令是否安全

    Args:
        cmd: 命令字符串

    Returns:
        bool: True 如果命令安全，否则 False
    """
    # 危险命令列表
    dangerous_commands = [
        "rm", "del", "format", "fdisk", "mkfs",
        "dd", "shutdown", "reboot", "halt",
        "passwd", "usermod", "userdel", "groupmod",
        "chmod", "chown", "mount", "umount",
        "sudo", "su", "visudo",
        "crontab", "at", "batch",
        "wget", "curl",  # 网络下载可能危险
        "ssh", "scp", "ftp", "sftp",  # 远程连接
        "python", "perl", "ruby", "bash", "sh", "zsh",  # 脚本执行
        "eval", "exec", "system",  # shell 内置命令
    ]

    # 检查是否包含危险命令
    cmd_lower = cmd.lower()
    for dangerous in dangerous_commands:
        if dangerous in cmd_lower:
            return False

    # 检查是否包含危险字符或模式
    dangerous_patterns = [
        "&&", "||", ";", "|", ">", "<", ">>", "<<",
        "$(", "`", "${", "$(",
        "2>", "2>>", "&>", "&>>",
        "rm -rf", "rm -r", "del /f", "del /q",
        "format", "fdisk", "mkfs",
    ]

    for pattern in dangerous_patterns:
        if pattern in cmd:
            return False

    return True


def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行系统命令

    Args:
        args: 包含以下字段的字典
            - cmd (str): 要执行的命令，必填
            - cwd (str, 可选): 当前工作目录
            - timeout (int, 可选): 超时时间（秒），默认为 60
            - env (dict, 可选): 环境变量字典
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"stdout": "...", "stderr": "...", "exit_code": 0}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 execute:command 权限
        - INVALID_INPUT: 输入参数无效或命令不安全
        - TIMEOUT: 命令执行超时
        - EXECUTION_ERROR: 命令执行失败
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
        cmd = args.get("cmd")
        user_id = args.get("user_id")

        if not cmd:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: cmd"
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
        if not check_permission(user_id, "execute:command"):
            logger.warning(f"用户 {user_id} 尝试执行命令但没有权限: {cmd}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有命令执行权限"
                }
            }

        # 命令安全检查
        if not _is_command_safe(cmd):
            logger.warning(f"用户 {user_id} 尝试执行不安全命令: {cmd}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "命令包含不安全内容或危险操作"
                }
            }

        # 获取可选参数
        cwd = args.get("cwd")
        timeout = args.get("timeout", 60)
        env = args.get("env")

        # 检查工作目录安全
        if cwd and not check_path_security(cwd):
            logger.warning(f"用户 {user_id} 尝试在不安全目录中执行命令: {cwd}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "工作目录不安全"
                }
            }

        # 执行命令
        try:
            logger.info(f"用户 {user_id} 开始执行命令: {cmd}")
            result = _run_command_with_timeout(cmd, cwd, env, timeout)

            # 检查执行结果
            if result["exit_code"] != 0 and result["stderr"]:
                logger.warning(f"命令执行失败 (exit_code={result['exit_code']}): {cmd}")
                return {
                    "success": False,
                    "error": {
                        "error_code": "EXECUTION_ERROR",
                        "message": f"命令执行失败: {result['stderr'][:200]}",
                        "details": {
                            "exit_code": result["exit_code"],
                            "stdout": result["stdout"][:500] if result["stdout"] else "",
                            "stderr": result["stderr"][:500] if result["stderr"] else ""
                        }
                    }
                }

            logger.info(f"用户 {user_id} 成功执行命令: {cmd}")
            return {
                "success": True,
                "output": {
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "exit_code": result["exit_code"]
                }
            }

        except CommandTimeoutError as e:
            logger.error(f"命令执行超时 {cmd}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "TIMEOUT",
                    "message": str(e)
                }
            }

        except Exception as e:
            logger.error(f"执行命令时发生未知错误 {cmd}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "EXECUTION_ERROR",
                    "message": f"命令执行时发生错误: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"命令执行工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "EXECUTION_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
