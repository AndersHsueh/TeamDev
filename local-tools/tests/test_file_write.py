"""
测试文件写入工具
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from ..tools.file_write import run


class TestFileWrite(unittest.TestCase):
    """测试 FileWrite 工具"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        self.test_content = "Hello, World!\nThis is test content."

    def tearDown(self):
        """测试后清理"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_successful_write(self):
        """测试成功写入文件"""
        args = {
            "path": self.test_file,
            "content": self.test_content,
            "user_id": "admin"
        }

        with patch('..tools.file_write.check_permission', return_value=True), \
             patch('..tools.file_write.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["path"], self.test_file)

        # 验证文件内容
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), self.test_content)

    def test_write_with_directory_creation(self):
        """测试写入文件时自动创建目录"""
        nested_file = os.path.join(self.temp_dir, "subdir", "nested", "file.txt")

        args = {
            "path": nested_file,
            "content": self.test_content,
            "user_id": "admin"
        }

        with patch('..tools.file_write.check_permission', return_value=True), \
             patch('..tools.file_write.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["path"], nested_file)

        # 验证文件内容
        with open(nested_file, 'r') as f:
            self.assertEqual(f.read(), self.test_content)

    def test_overwrite_existing_file(self):
        """测试覆盖现有文件"""
        # 先创建文件
        with open(self.test_file, 'w') as f:
            f.write("original content")

        new_content = "new content"

        args = {
            "path": self.test_file,
            "content": new_content,
            "overwrite": True,
            "user_id": "admin"
        }

        with patch('..tools.file_write.check_permission', return_value=True), \
             patch('..tools.file_write.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])

        # 验证文件内容被覆盖
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), new_content)

    def test_overwrite_false_existing_file(self):
        """测试不允许覆盖现有文件"""
        # 先创建文件
        with open(self.test_file, 'w') as f:
            f.write("original content")

        args = {
            "path": self.test_file,
            "content": "new content",
            "overwrite": False,
            "user_id": "admin"
        }

        with patch('..tools.file_write.check_permission', return_value=True), \
             patch('..tools.file_write.check_path_security', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "ALREADY_EXISTS")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "path": self.test_file,
            "content": self.test_content,
            "user_id": "user"
        }

        with patch('..tools.file_write.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")

    def test_invalid_path_security(self):
        """测试路径不安全"""
        args = {
            "path": "/etc/passwd",
            "content": self.test_content,
            "user_id": "admin"
        }

        with patch('..tools.file_write.check_permission', return_value=True), \
             patch('..tools.file_write.check_path_security', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_missing_required_args(self):
        """测试缺少必需参数"""
        # 缺少 path
        args = {"content": self.test_content, "user_id": "admin"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        # 缺少 content
        args = {"path": self.test_file, "user_id": "admin"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        # 缺少 user_id
        args = {"path": self.test_file, "content": self.test_content}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")


if __name__ == '__main__':
    unittest.main()
