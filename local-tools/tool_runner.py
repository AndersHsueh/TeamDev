"""
工具调度器
统一调度和管理所有工具的执行
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from tools import (
    file_read_run,
    file_write_run,
    file_delete_run,
    list_directory_run,
    execute_command_run,
    http_request_run
)

logger = logging.getLogger(__name__)


class ToolRunner:
    """
    工具调度器类
    负责调度和执行各种工具
    """

    def __init__(self):
        # 工具映射
        self._tools = {
            "FileRead": file_read_run,
            "FileWrite": file_write_run,
            "FileDelete": file_delete_run,
            "ListDirectory": list_directory_run,
            "ExecuteCommand": execute_command_run,
            "HttpRequest": http_request_run
        }

        # 调用日志
        self._call_log = []

    def list_available_tools(self) -> Dict[str, str]:
        """
        获取所有可用工具的列表

        Returns:
            Dict[str, str]: 工具名到描述的映射
        """
        return {
            "FileRead": "读取文件内容",
            "FileWrite": "写入文件内容",
            "FileDelete": "删除文件或目录",
            "ListDirectory": "列举目录内容",
            "ExecuteCommand": "执行系统命令",
            "HttpRequest": "发送 HTTP 请求"
        }

    def run_tool(self, request: Dict[str, Any], caller_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行工具

        Args:
            request: 工具调用请求
                {
                    "tool": "ToolName",
                    "args": {...}
                }
            caller_info: 调用者信息（可选）
                {
                    "user_id": "user123",
                    "session_id": "session456",
                    "ip_address": "192.168.1.1"
                }

        Returns:
            Dict: 标准响应格式
        """
        start_time = time.time()
        tool_name = None
        user_id = "unknown"

        try:
            # 验证请求格式
            if not isinstance(request, dict):
                return self._create_error_response(
                    "INVALID_INPUT",
                    "请求必须是字典类型",
                    tool_name,
                    user_id
                )

            # 提取工具名
            tool_name = request.get("tool")
            if not tool_name:
                return self._create_error_response(
                    "INVALID_INPUT",
                    "缺少必需字段: tool",
                    tool_name,
                    user_id
                )

            # 检查工具是否存在
            if tool_name not in self._tools:
                available_tools = list(self._tools.keys())
                return self._create_error_response(
                    "INVALID_INPUT",
                    f"未知工具 '{tool_name}'，可用工具: {available_tools}",
                    tool_name,
                    user_id
                )

            # 提取参数
            args = request.get("args", {})
            if not isinstance(args, dict):
                return self._create_error_response(
                    "INVALID_INPUT",
                    "args 字段必须是字典类型",
                    tool_name,
                    user_id
                )

            # 获取用户ID
            if caller_info and "user_id" in caller_info:
                user_id = caller_info["user_id"]
            elif "user_id" in args:
                user_id = args["user_id"]
            else:
                return self._create_error_response(
                    "INVALID_INPUT",
                    "缺少用户ID信息",
                    tool_name,
                    user_id
                )

            # 执行工具
            logger.info(f"开始执行工具: {tool_name}, 用户: {user_id}")
            result = self._tools[tool_name](args)

            # 记录调用日志
            execution_time = time.time() - start_time
            self._log_call(tool_name, user_id, args, result, execution_time, caller_info)

            logger.info(f"工具执行完成: {tool_name}, 耗时: {execution_time:.2f}s")
            return result

        except Exception as e:
            # 记录异常日志
            execution_time = time.time() - start_time
            error_result = self._create_error_response(
                "EXECUTION_ERROR",
                f"工具调度器执行失败: {str(e)}",
                tool_name,
                user_id
            )

            self._log_call(tool_name, user_id, request.get("args", {}), error_result, execution_time, caller_info)

            logger.error(f"工具调度器执行异常: {e}", exc_info=True)
            return error_result

    def _create_error_response(self, error_code: str, message: str,
                             tool_name: Optional[str] = None,
                             user_id: str = "unknown") -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            error_code: 错误码
            message: 错误消息
            tool_name: 工具名
            user_id: 用户ID

        Returns:
            Dict: 错误响应
        """
        logger.warning(f"工具调用错误 [{error_code}]: {message} (工具: {tool_name}, 用户: {user_id})")

        return {
            "success": False,
            "error": {
                "error_code": error_code,
                "message": message,
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _log_call(self, tool_name: Optional[str], user_id: str, args: Dict[str, Any],
                  result: Dict[str, Any], execution_time: float,
                  caller_info: Optional[Dict[str, Any]] = None):
        """
        记录工具调用日志

        Args:
            tool_name: 工具名
            user_id: 用户ID
            args: 调用参数（脱敏）
            result: 执行结果
            execution_time: 执行时间
            caller_info: 调用者信息
        """
        # 脱敏敏感信息
        safe_args = self._sanitize_args(args)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "user_id": user_id,
            "args": safe_args,
            "success": result.get("success", False),
            "error_code": result.get("error", {}).get("error_code"),
            "execution_time": round(execution_time, 3),
            "caller_info": caller_info
        }

        self._call_log.append(log_entry)

        # 限制日志大小
        if len(self._call_log) > 1000:
            self._call_log = self._call_log[-500:]  # 保留最新的500条

    def _sanitize_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱敏参数中的敏感信息

        Args:
            args: 原始参数

        Returns:
            Dict: 脱敏后的参数
        """
        safe_args = args.copy()

        # 隐藏敏感字段
        sensitive_fields = ["password", "token", "secret", "key", "auth"]

        for field in sensitive_fields:
            if field in safe_args:
                safe_args[field] = "***"

        return safe_args

    def get_call_history(self, user_id: Optional[str] = None,
                        tool_name: Optional[str] = None,
                        limit: int = 50) -> list:
        """
        获取调用历史

        Args:
            user_id: 过滤特定用户的调用记录
            tool_name: 过滤特定工具的调用记录
            limit: 返回记录的最大数量

        Returns:
            list: 调用历史记录
        """
        filtered_logs = self._call_log

        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]

        if tool_name:
            filtered_logs = [log for log in filtered_logs if log["tool"] == tool_name]

        return filtered_logs[-limit:]

    def clear_call_history(self):
        """清空调用历史"""
        self._call_log.clear()
        logger.info("调用历史已清空")


# 全局工具调度器实例
_tool_runner = None


def get_tool_runner() -> ToolRunner:
    """获取全局工具调度器实例"""
    global _tool_runner
    if _tool_runner is None:
        _tool_runner = ToolRunner()
    return _tool_runner


def run_tool(request: Dict[str, Any], caller_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    执行工具的便捷函数

    Args:
        request: 工具调用请求
        caller_info: 调用者信息

    Returns:
        Dict: 工具执行结果
    """
    return get_tool_runner().run_tool(request, caller_info)
