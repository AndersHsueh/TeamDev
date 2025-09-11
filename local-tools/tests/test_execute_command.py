"""
测试命令执行工具
"""

import unittest
from unittest.mock import patch

from ..tools.execute_command import run


class TestExecuteCommand(unittest.TestCase):
    """测试 ExecuteCommand 工具"""

    def test_successful_command(self):
        """测试成功执行命令"""
        args = {
            "cmd": "echo 'Hello World'",
            "user_id": "admin"
        }

        with patch('..tools.execute_command.check_permission', return_value=True), \
             patch('..tools.execute_command.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["stdout"].strip(), "Hello World")
        self.assertEqual(result["output"]["exit_code"], 0)

    def test_command_with_timeout(self):
        """测试命令执行超时"""
        # 使用一个会运行较长时间的命令
        args = {
            "cmd": "sleep 2",
            "timeout": 1,  # 1秒超时
            "user_id": "admin"
        }

        with patch('..tools.execute_command.check_permission', return_value=True), \
             patch('..tools.execute_command.check_path_security', return_value=True):

            result = run(args)

        # 应该超时并返回错误
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "TIMEOUT")

    def test_dangerous_command(self):
        """测试危险命令被拒绝"""
        args = {
            "cmd": "rm -rf /",
            "user_id": "admin"
        }

        with patch('..tools.execute_command.check_permission', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "cmd": "echo test",
            "user_id": "user"
        }

        with patch('..tools.execute_command.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")

    def test_missing_required_args(self):
        """测试缺少必需参数"""
        # 缺少 cmd
        args = {"user_id": "admin"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        # 缺少 user_id
        args = {"cmd": "echo test"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")


if __name__ == '__main__':
    unittest.main()
