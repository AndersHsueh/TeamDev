"""
测试文件删除工具
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from ..tools.file_delete import run


class TestFileDelete(unittest.TestCase):
    """测试 FileDelete 工具"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        self.test_dir = os.path.join(self.temp_dir, "test_dir")

        # 创建测试文件
        with open(self.test_file, 'w') as f:
            f.write("test content")

        # 创建测试目录
        os.makedirs(self.test_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_delete_file(self):
        """测试删除文件"""
        args = {
            "path": self.test_file,
            "user_id": "admin"
        }

        with patch('..tools.file_delete.check_permission', return_value=True), \
             patch('..tools.file_delete.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertFalse(os.path.exists(self.test_file))

    def test_delete_empty_directory(self):
        """测试删除空目录"""
        args = {
            "path": self.test_dir,
            "recursive": False,
            "user_id": "admin"
        }

        with patch('..tools.file_delete.check_permission', return_value=True), \
             patch('..tools.file_delete.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertFalse(os.path.exists(self.test_dir))

    def test_delete_directory_recursive(self):
        """测试递归删除目录"""
        # 在目录中创建文件
        nested_file = os.path.join(self.test_dir, "nested_file.txt")
        with open(nested_file, 'w') as f:
            f.write("nested content")

        args = {
            "path": self.test_dir,
            "recursive": True,
            "user_id": "admin"
        }

        with patch('..tools.file_delete.check_permission', return_value=True), \
             patch('..tools.file_delete.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertFalse(os.path.exists(self.test_dir))

    def test_delete_nonexistent_path(self):
        """测试删除不存在的路径"""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent")

        args = {
            "path": nonexistent_path,
            "user_id": "admin"
        }

        with patch('..tools.file_delete.check_permission', return_value=True), \
             patch('..tools.file_delete.check_path_security', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "NOT_FOUND")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "path": self.test_file,
            "user_id": "user"
        }

        with patch('..tools.file_delete.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")


if __name__ == '__main__':
    unittest.main()
