"""
测试文件读取工具
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from ..tools.file_read import run


class TestFileRead(unittest.TestCase):
    """测试 FileRead 工具"""

    def setUp(self):
        """测试前准备"""
        self.test_content = "Hello, World!\nThis is a test file."
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.test_file.write(self.test_content)
        self.test_file.close()

        # 创建一个不存在的文件路径
        self.nonexistent_file = "/tmp/nonexistent_file_12345.txt"

    def tearDown(self):
        """测试后清理"""
        try:
            os.unlink(self.test_file.name)
        except:
            pass

    def test_successful_read(self):
        """测试成功读取文件"""
        args = {
            "path": self.test_file.name,
            "encoding": "utf-8",
            "user_id": "admin"
        }

        with patch('..tools.file_read.check_permission', return_value=True), \
             patch('..tools.file_read.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["content"], self.test_content)

    def test_file_not_found(self):
        """测试文件不存在"""
        args = {
            "path": self.nonexistent_file,
            "user_id": "admin"
        }

        with patch('..tools.file_read.check_permission', return_value=True), \
             patch('..tools.file_read.check_path_security', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "NOT_FOUND")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "path": self.test_file.name,
            "user_id": "user"
        }

        with patch('..tools.file_read.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")

    def test_invalid_path_security(self):
        """测试路径不安全"""
        args = {
            "path": "/etc/passwd",
            "user_id": "admin"
        }

        with patch('..tools.file_read.check_permission', return_value=True), \
             patch('..tools.file_read.check_path_security', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_missing_required_args(self):
        """测试缺少必需参数"""
        # 缺少 path
        args = {"user_id": "admin"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        # 缺少 user_id
        args = {"path": self.test_file.name}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_invalid_input_type(self):
        """测试无效输入类型"""
        result = run("not a dict")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_directory_as_file(self):
        """测试将目录当作文件读取"""
        temp_dir = tempfile.mkdtemp()

        args = {
            "path": temp_dir,
            "user_id": "admin"
        }

        with patch('..tools.file_read.check_permission', return_value=True), \
             patch('..tools.file_read.check_path_security', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        os.rmdir(temp_dir)


if __name__ == '__main__':
    unittest.main()
