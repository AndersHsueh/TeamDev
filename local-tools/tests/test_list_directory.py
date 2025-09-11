"""
测试目录列举工具
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from ..tools.list_directory import run


class TestListDirectory(unittest.TestCase):
    """测试 ListDirectory 工具"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        self.hidden_file = os.path.join(self.temp_dir, ".hidden_file")
        self.test_dir = os.path.join(self.temp_dir, "test_subdir")

        # 创建测试文件
        with open(self.test_file, 'w') as f:
            f.write("test content")

        with open(self.hidden_file, 'w') as f:
            f.write("hidden content")

        # 创建测试目录
        os.makedirs(self.test_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_list_directory(self):
        """测试列举目录内容"""
        args = {
            "path": self.temp_dir,
            "user_id": "admin"
        }

        with patch('..tools.list_directory.check_permission', return_value=True), \
             patch('..tools.list_directory.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        entries = result["output"]["entries"]

        # 检查是否包含测试文件和目录
        file_names = [entry["name"] for entry in entries]
        self.assertIn("test_file.txt", file_names)
        self.assertIn("test_subdir", file_names)

    def test_list_directory_include_hidden(self):
        """测试包含隐藏文件"""
        args = {
            "path": self.temp_dir,
            "include_hidden": True,
            "user_id": "admin"
        }

        with patch('..tools.list_directory.check_permission', return_value=True), \
             patch('..tools.list_directory.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        entries = result["output"]["entries"]

        # 检查是否包含隐藏文件
        file_names = [entry["name"] for entry in entries]
        self.assertIn(".hidden_file", file_names)

    def test_list_directory_exclude_hidden(self):
        """测试排除隐藏文件"""
        args = {
            "path": self.temp_dir,
            "include_hidden": False,
            "user_id": "admin"
        }

        with patch('..tools.list_directory.check_permission', return_value=True), \
             patch('..tools.list_directory.check_path_security', return_value=True):

            result = run(args)

        self.assertTrue(result["success"])
        entries = result["output"]["entries"]

        # 检查是否不包含隐藏文件
        file_names = [entry["name"] for entry in entries]
        self.assertNotIn(".hidden_file", file_names)

    def test_list_nonexistent_directory(self):
        """测试列举不存在的目录"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")

        args = {
            "path": nonexistent_dir,
            "user_id": "admin"
        }

        with patch('..tools.list_directory.check_permission', return_value=True), \
             patch('..tools.list_directory.check_path_security', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "NOT_FOUND")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "path": self.temp_dir,
            "user_id": "user"
        }

        with patch('..tools.list_directory.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")


if __name__ == '__main__':
    unittest.main()
