"""
文件浏览器组件单元测试
"""

import unittest
import sys
import os
import tempfile
import shutil

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.file_explorer import FileExplorerComponent, FileNode


class TestFileExplorerComponent(unittest.TestCase):
    """文件浏览器组件测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.component = FileExplorerComponent("test_file_explorer")
        
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_structure()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_structure(self):
        """创建测试目录结构"""
        # 创建文件和目录
        os.makedirs(os.path.join(self.temp_dir, "subdir1"))
        os.makedirs(os.path.join(self.temp_dir, "subdir2"))
        
        # 创建文件
        with open(os.path.join(self.temp_dir, "file1.txt"), "w") as f:
            f.write("test content 1")
        
        with open(os.path.join(self.temp_dir, "file2.py"), "w") as f:
            f.write("print('hello world')")
        
        with open(os.path.join(self.temp_dir, "subdir1", "file3.md"), "w") as f:
            f.write("# Test Markdown")
        
        # 创建隐藏文件
        with open(os.path.join(self.temp_dir, ".hidden_file"), "w") as f:
            f.write("hidden content")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.component.name, "test_file_explorer")
        self.assertEqual(self.component.root_path, ".")
        self.assertIsNone(self.component.root_node)
        self.assertEqual(self.component.scroll_offset, 0)
        self.assertTrue(self.component.hidden_files)
        self.assertIsNone(self.component.file_filter)
    
    def test_set_root_path(self):
        """测试设置根路径"""
        self.component.set_root_path(self.temp_dir)
        self.assertEqual(self.component.root_path, self.temp_dir)
        self.assertIsNotNone(self.component.root_node)
        self.assertEqual(self.component.root_node.path, self.temp_dir)
        self.assertTrue(self.component.root_node.is_dir)
    
    def test_set_hidden_files(self):
        """测试设置隐藏文件显示"""
        self.component.set_root_path(self.temp_dir)
        
        # 显示隐藏文件
        self.component.set_hidden_files(True)
        visible_nodes = self.component._get_visible_nodes()
        hidden_found = any(node.name.startswith('.') for node in visible_nodes)
        self.assertTrue(hidden_found)
        
        # 隐藏文件
        self.component.set_hidden_files(False)
        visible_nodes = self.component._get_visible_nodes()
        hidden_found = any(node.name.startswith('.') for node in visible_nodes)
        self.assertFalse(hidden_found)
    
    def test_set_file_filter(self):
        """测试设置文件过滤器"""
        self.component.set_root_path(self.temp_dir)
        
        # 只显示 Python 文件
        def python_filter(path):
            return path.endswith('.py')
        
        self.component.set_file_filter(python_filter)
        visible_nodes = self.component._get_visible_nodes()
        
        # 检查是否只包含 Python 文件
        for node in visible_nodes:
            if not node.is_dir:
                self.assertTrue(node.name.endswith('.py'))
    
    def test_file_node_creation(self):
        """测试文件节点创建"""
        # 测试目录节点
        dir_node = FileNode(self.temp_dir, "test_dir", True)
        self.assertEqual(dir_node.path, self.temp_dir)
        self.assertEqual(dir_node.name, "test_dir")
        self.assertTrue(dir_node.is_dir)
        self.assertFalse(dir_node.expanded)
        self.assertFalse(dir_node.selected)
        
        # 测试文件节点
        file_path = os.path.join(self.temp_dir, "test.txt")
        file_node = FileNode(file_path, "test.txt", False)
        self.assertEqual(file_node.path, file_path)
        self.assertEqual(file_node.name, "test.txt")
        self.assertFalse(file_node.is_dir)
    
    def test_file_node_icon(self):
        """测试文件节点图标"""
        # 目录图标
        dir_node = FileNode("/path/to/dir", "dir", True)
        self.assertIn(dir_node.get_icon(), ["📁", "📂"])
        
        # 文件图标
        py_file = FileNode("/path/to/file.py", "file.py", False)
        self.assertEqual(py_file.get_icon(), "🐍")
        
        txt_file = FileNode("/path/to/file.txt", "file.txt", False)
        self.assertEqual(txt_file.get_icon(), "📄")
    
    def test_render_basic(self):
        """测试基本渲染"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(50, 10)
        
        rendered = self.component.render()
        
        # 检查渲染结果
        self.assertIsInstance(rendered, str)
        self.assertGreater(len(rendered), 0)
        
        # 检查包含目录和文件
        lines = rendered.split('\n')
        self.assertGreater(len(lines), 0)
    
    def test_render_with_selection(self):
        """测试带选择的渲染"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(50, 10)
        
        # 选择第一个节点
        visible_nodes = self.component._get_visible_nodes()
        if visible_nodes:
            visible_nodes[0].selected = True
        
        rendered = self.component.render()
        self.assertIsInstance(rendered, str)
    
    def test_handle_key_navigation(self):
        """测试键盘导航"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(50, 10)
        
        # 测试向下移动
        result = self.component.handle_key("down")
        self.assertTrue(result)
        
        # 测试向上移动
        result = self.component.handle_key("up")
        self.assertTrue(result)
        
        # 测试回车键
        result = self.component.handle_key("enter")
        self.assertTrue(result)
    
    def test_handle_key_expand_collapse(self):
        """测试展开/折叠功能"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(50, 10)
        
        # 找到第一个目录
        visible_nodes = self.component._get_visible_nodes()
        dir_node = None
        for node in visible_nodes:
            if node.is_dir:
                dir_node = node
                break
        
        if dir_node:
            # 展开目录
            result = self.component.handle_key("right")
            self.assertTrue(result)
            
            # 折叠目录
            result = self.component.handle_key("left")
            self.assertTrue(result)
    
    def test_handle_mouse(self):
        """测试鼠标处理"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(50, 10)
        
        # 测试鼠标点击
        result = self.component.handle_mouse(5, 2, 1)
        self.assertTrue(result)
    
    def test_get_selected_path(self):
        """测试获取选中路径"""
        self.component.set_root_path(self.temp_dir)
        
        # 选择第一个节点
        visible_nodes = self.component._get_visible_nodes()
        if visible_nodes:
            visible_nodes[0].selected = True
            selected_path = self.component.get_selected_path()
            self.assertIsNotNone(selected_path)
            self.assertEqual(selected_path, visible_nodes[0].path)
    
    def test_expand_path(self):
        """测试展开路径"""
        self.component.set_root_path(self.temp_dir)
        
        # 展开到子目录
        subdir_path = os.path.join(self.temp_dir, "subdir1")
        result = self.component.expand_path(subdir_path)
        self.assertTrue(result)
        
        # 检查子目录是否展开
        visible_nodes = self.component._get_visible_nodes()
        subdir_found = any(node.path == subdir_path for node in visible_nodes)
        self.assertTrue(subdir_found)
    
    def test_expand_invalid_path(self):
        """测试展开无效路径"""
        self.component.set_root_path(self.temp_dir)
        
        # 尝试展开不存在的路径
        invalid_path = os.path.join(self.temp_dir, "nonexistent")
        result = self.component.expand_path(invalid_path)
        self.assertFalse(result)
    
    def test_update_with_dict(self):
        """测试使用字典更新"""
        update_data = {
            "root_path": self.temp_dir,
            "hidden_files": False
        }
        
        self.component.update(update_data)
        
        self.assertEqual(self.component.root_path, self.temp_dir)
        self.assertFalse(self.component.hidden_files)
    
    def test_file_select_callback(self):
        """测试文件选择回调"""
        selected_files = []
        
        def callback(file_path):
            selected_files.append(file_path)
        
        self.component.set_file_select_callback(callback)
        self.component.set_root_path(self.temp_dir)
        
        # 模拟选择文件
        visible_nodes = self.component._get_visible_nodes()
        file_node = None
        for node in visible_nodes:
            if not node.is_dir:
                file_node = node
                break
        
        if file_node:
            self.component._select_node_at_index(0)
            self.component.handle_key("enter")
            
            # 检查回调是否被调用
            self.assertGreater(len(selected_files), 0)
            self.assertEqual(selected_files[0], file_node.path)
    
    def test_dir_expand_callback(self):
        """测试目录展开回调"""
        expanded_dirs = []
        
        def callback(dir_path):
            expanded_dirs.append(dir_path)
        
        self.component.set_dir_expand_callback(callback)
        self.component.set_root_path(self.temp_dir)
        
        # 模拟展开目录
        visible_nodes = self.component._get_visible_nodes()
        dir_node = None
        for node in visible_nodes:
            if node.is_dir:
                dir_node = node
                break
        
        if dir_node:
            self.component._select_node_at_index(0)
            self.component.handle_key("enter")
            
            # 检查回调是否被调用
            self.assertGreater(len(expanded_dirs), 0)
            self.assertEqual(expanded_dirs[0], dir_node.path)
    
    def test_size_constraints(self):
        """测试尺寸约束"""
        self.component.set_root_path(self.temp_dir)
        self.component.set_size(20, 5)
        
        rendered = self.component.render()
        lines = rendered.split('\n')
        
        # 检查行数不超过指定高度
        self.assertLessEqual(len(lines), 5)
        
        # 检查每行长度不超过指定宽度
        for line in lines:
            self.assertLessEqual(len(line), 20)


if __name__ == "__main__":
    unittest.main()
