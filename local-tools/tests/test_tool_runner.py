"""
测试工具调度器
"""

import unittest
from unittest.mock import patch

from ..tool_runner import ToolRunner


class TestToolRunner(unittest.TestCase):
    """测试 ToolRunner 类"""

    def setUp(self):
        """测试前准备"""
        self.runner = ToolRunner()

    def test_list_available_tools(self):
        """测试获取可用工具列表"""
        tools = self.runner.list_available_tools()

        expected_tools = {
            "FileRead": "读取文件内容",
            "FileWrite": "写入文件内容",
            "FileDelete": "删除文件或目录",
            "ListDirectory": "列举目录内容",
            "ExecuteCommand": "执行系统命令",
            "HttpRequest": "发送 HTTP 请求"
        }

        self.assertEqual(tools, expected_tools)

    def test_run_tool_success(self):
        """测试成功执行工具"""
        request = {
            "tool": "FileRead",
            "args": {
                "path": "/tmp/test.txt",
                "user_id": "admin"
            }
        }

        mock_result = {
            "success": True,
            "output": {"content": "test content"}
        }

        with patch.object(self.runner, '_ToolRunner__tools') as mock_tools:
            mock_tools.__getitem__.return_value = lambda args: mock_result

            result = self.runner.run_tool(request)

        self.assertEqual(result, mock_result)

    def test_run_tool_unknown_tool(self):
        """测试未知工具"""
        request = {
            "tool": "UnknownTool",
            "args": {"user_id": "admin"}
        }

        result = self.runner.run_tool(request)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")
        self.assertIn("未知工具", result["error"]["message"])

    def test_run_tool_missing_tool(self):
        """测试缺少工具名"""
        request = {
            "args": {"user_id": "admin"}
        }

        result = self.runner.run_tool(request)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")
        self.assertIn("缺少必需字段: tool", result["error"]["message"])

    def test_run_tool_invalid_request_format(self):
        """测试无效请求格式"""
        request = "not a dict"

        result = self.runner.run_tool(request)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_run_tool_missing_args(self):
        """测试缺少参数"""
        request = {
            "tool": "FileRead"
            # 缺少 args
        }

        result = self.runner.run_tool(request)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_call_history(self):
        """测试调用历史记录"""
        # 清空历史
        self.runner.clear_call_history()

        request = {
            "tool": "FileRead",
            "args": {
                "path": "/tmp/test.txt",
                "user_id": "admin"
            }
        }

        mock_result = {
            "success": True,
            "output": {"content": "test content"}
        }

        with patch.object(self.runner, '_ToolRunner__tools') as mock_tools:
            mock_tools.__getitem__.return_value = lambda args: mock_result

            # 执行工具
            self.runner.run_tool(request)

        # 检查调用历史
        history = self.runner.get_call_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["tool"], "FileRead")
        self.assertEqual(history[0]["user_id"], "admin")
        self.assertTrue(history[0]["success"])

    def test_call_history_filtering(self):
        """测试调用历史过滤"""
        # 清空历史
        self.runner.clear_call_history()

        # 添加多个调用记录
        with patch.object(self.runner, '_ToolRunner__tools') as mock_tools:
            mock_tools.__getitem__.return_value = lambda args: {"success": True, "output": {}}

            self.runner.run_tool({
                "tool": "FileRead",
                "args": {"user_id": "admin", "path": "/tmp/test1.txt"}
            })

            self.runner.run_tool({
                "tool": "FileWrite",
                "args": {"user_id": "user", "path": "/tmp/test2.txt"}
            })

        # 过滤用户
        admin_history = self.runner.get_call_history(user_id="admin")
        self.assertEqual(len(admin_history), 1)
        self.assertEqual(admin_history[0]["tool"], "FileRead")

        # 过滤工具
        fileread_history = self.runner.get_call_history(tool_name="FileRead")
        self.assertEqual(len(fileread_history), 1)
        self.assertEqual(fileread_history[0]["user_id"], "admin")


if __name__ == '__main__':
    unittest.main()
