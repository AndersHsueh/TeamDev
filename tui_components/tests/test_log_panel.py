"""
日志面板组件单元测试
"""

import unittest
import sys
import os
import tempfile

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.log_panel import LogPanelComponent, LogLevel, LogEntry


class TestLogPanelComponent(unittest.TestCase):
    """日志面板组件测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.component = LogPanelComponent("test_log_panel")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.component.name, "test_log_panel")
        self.assertEqual(len(self.component.logs), 0)
        self.assertEqual(self.component.max_logs, 1000)
        self.assertEqual(self.component.scroll_offset, 0)
        self.assertTrue(self.component.auto_scroll)
        self.assertTrue(self.component.show_timestamp)
        self.assertTrue(self.component.show_level)
        self.assertFalse(self.component.show_source)
        self.assertTrue(self.component.word_wrap)
        self.assertEqual(len(self.component.filter_levels), len(LogLevel))
        self.assertIsNone(self.component.filter_source)
    
    def test_add_log(self):
        """测试添加日志"""
        self.component.add_log(LogLevel.INFO, "测试信息", "test_source")
        
        self.assertEqual(len(self.component.logs), 1)
        log = self.component.logs[0]
        self.assertEqual(log.level, LogLevel.INFO)
        self.assertEqual(log.message, "测试信息")
        self.assertEqual(log.source, "test_source")
    
    def test_add_log_methods(self):
        """测试各种添加日志的方法"""
        # 测试各种级别的日志
        self.component.add_debug("调试信息")
        self.component.add_info("信息")
        self.component.add_warning("警告")
        self.component.add_error("错误")
        self.component.add_critical("严重错误")
        
        self.assertEqual(len(self.component.logs), 5)
        self.assertEqual(self.component.logs[0].level, LogLevel.DEBUG)
        self.assertEqual(self.component.logs[1].level, LogLevel.INFO)
        self.assertEqual(self.component.logs[2].level, LogLevel.WARNING)
        self.assertEqual(self.component.logs[3].level, LogLevel.ERROR)
        self.assertEqual(self.component.logs[4].level, LogLevel.CRITICAL)
    
    def test_clear_logs(self):
        """测试清空日志"""
        self.component.add_info("测试信息")
        self.component.add_error("测试错误")
        
        self.assertEqual(len(self.component.logs), 2)
        
        self.component.clear_logs()
        
        self.assertEqual(len(self.component.logs), 0)
        self.assertEqual(self.component.scroll_offset, 0)
    
    def test_set_max_logs(self):
        """测试设置最大日志数"""
        self.component.set_max_logs(5)
        self.assertEqual(self.component.max_logs, 5)
        
        # 添加超过最大数量的日志
        for i in range(10):
            self.component.add_info(f"日志 {i}")
        
        # 检查是否只保留最后5条
        self.assertEqual(len(self.component.logs), 5)
        self.assertEqual(self.component.logs[0].message, "日志 5")
        self.assertEqual(self.component.logs[-1].message, "日志 9")
    
    def test_set_auto_scroll(self):
        """测试设置自动滚动"""
        self.component.set_auto_scroll(False)
        self.assertFalse(self.component.auto_scroll)
        
        self.component.set_auto_scroll(True)
        self.assertTrue(self.component.auto_scroll)
    
    def test_set_display_options(self):
        """测试设置显示选项"""
        self.component.set_display_options(
            show_timestamp=False,
            show_level=False,
            show_source=True,
            word_wrap=False
        )
        
        self.assertFalse(self.component.show_timestamp)
        self.assertFalse(self.component.show_level)
        self.assertTrue(self.component.show_source)
        self.assertFalse(self.component.word_wrap)
    
    def test_set_filter_levels(self):
        """测试设置过滤级别"""
        # 只显示错误和警告
        self.component.set_filter_levels([LogLevel.ERROR, LogLevel.WARNING])
        
        self.component.add_info("信息")
        self.component.add_warning("警告")
        self.component.add_error("错误")
        
        filtered_logs = self.component._get_filtered_logs()
        self.assertEqual(len(filtered_logs), 2)
        self.assertEqual(filtered_logs[0].level, LogLevel.WARNING)
        self.assertEqual(filtered_logs[1].level, LogLevel.ERROR)
    
    def test_set_filter_source(self):
        """测试设置过滤来源"""
        self.component.set_filter_source("test_source")
        
        self.component.add_info("信息1", "test_source")
        self.component.add_info("信息2", "other_source")
        self.component.add_error("错误", "test_source")
        
        filtered_logs = self.component._get_filtered_logs()
        self.assertEqual(len(filtered_logs), 2)
        self.assertEqual(filtered_logs[0].message, "信息1")
        self.assertEqual(filtered_logs[1].message, "错误")
    
    def test_scroll_methods(self):
        """测试滚动方法"""
        # 添加一些日志
        for i in range(10):
            self.component.add_info(f"日志 {i}")
        
        # 滚动到底部
        self.component.scroll_to_bottom()
        self.assertGreater(self.component.scroll_offset, 0)
        
        # 滚动到顶部
        self.component.scroll_to_top()
        self.assertEqual(self.component.scroll_offset, 0)
    
    def test_render_basic(self):
        """测试基本渲染"""
        self.component.add_info("测试信息")
        self.component.add_error("测试错误")
        self.component.set_size(50, 10)
        
        rendered = self.component.render()
        
        # 检查渲染结果
        self.assertIsInstance(rendered, str)
        self.assertGreater(len(rendered), 0)
        
        # 检查包含日志内容
        self.assertIn("测试信息", rendered)
        self.assertIn("测试错误", rendered)
    
    def test_render_with_filters(self):
        """测试带过滤的渲染"""
        self.component.add_info("信息")
        self.component.add_warning("警告")
        self.component.add_error("错误")
        
        # 只显示错误
        self.component.set_filter_levels([LogLevel.ERROR])
        self.component.set_size(50, 10)
        
        rendered = self.component.render()
        
        # 检查只包含错误日志
        self.assertIn("错误", rendered)
        self.assertNotIn("信息", rendered)
        self.assertNotIn("警告", rendered)
    
    def test_render_with_timestamp(self):
        """测试带时间戳的渲染"""
        self.component.add_info("测试信息")
        self.component.set_size(50, 10)
        
        rendered = self.component.render()
        
        # 检查包含时间戳
        self.assertIn(":", rendered)  # 时间戳包含冒号
    
    def test_render_without_timestamp(self):
        """测试不带时间戳的渲染"""
        self.component.set_display_options(show_timestamp=False)
        self.component.add_info("测试信息")
        self.component.set_size(50, 10)
        
        rendered = self.component.render()
        
        # 检查不包含时间戳
        self.assertIn("测试信息", rendered)
    
    def test_handle_key_navigation(self):
        """测试键盘导航"""
        # 添加一些日志
        for i in range(10):
            self.component.add_info(f"日志 {i}")
        
        self.component.set_size(50, 5)
        
        # 测试向下滚动
        result = self.component.handle_key("down")
        self.assertTrue(result)
        self.assertGreater(self.component.scroll_offset, 0)
        
        # 测试向上滚动
        result = self.component.handle_key("up")
        self.assertTrue(result)
        self.assertEqual(self.component.scroll_offset, 0)
    
    def test_handle_key_page_navigation(self):
        """测试页面导航"""
        # 添加一些日志
        for i in range(20):
            self.component.add_info(f"日志 {i}")
        
        self.component.set_size(50, 5)
        
        # 测试向下翻页
        result = self.component.handle_key("page_down")
        self.assertTrue(result)
        self.assertGreater(self.component.scroll_offset, 0)
        
        # 测试向上翻页
        result = self.component.handle_key("page_up")
        self.assertTrue(result)
        self.assertEqual(self.component.scroll_offset, 0)
    
    def test_handle_key_home_end(self):
        """测试 Home/End 键"""
        # 添加一些日志
        for i in range(10):
            self.component.add_info(f"日志 {i}")
        
        self.component.set_size(50, 5)
        
        # 滚动到底部
        self.component.scroll_to_bottom()
        
        # 测试 Home 键
        result = self.component.handle_key("home")
        self.assertTrue(result)
        self.assertEqual(self.component.scroll_offset, 0)
        
        # 测试 End 键
        result = self.component.handle_key("end")
        self.assertTrue(result)
        self.assertGreater(self.component.scroll_offset, 0)
    
    def test_handle_key_clear(self):
        """测试清空日志"""
        self.component.add_info("测试信息")
        self.component.add_error("测试错误")
        
        self.assertEqual(len(self.component.logs), 2)
        
        result = self.component.handle_key("c")
        self.assertTrue(result)
        
        self.assertEqual(len(self.component.logs), 0)
    
    def test_handle_mouse(self):
        """测试鼠标处理"""
        # 添加一些日志
        for i in range(10):
            self.component.add_info(f"日志 {i}")
        
        self.component.set_size(50, 5)
        
        # 测试鼠标滚轮向上
        result = self.component.handle_mouse(10, 5, 4)
        self.assertTrue(result)
        
        # 测试鼠标滚轮向下
        result = self.component.handle_mouse(10, 5, 5)
        self.assertTrue(result)
    
    def test_update_with_dict(self):
        """测试使用字典更新"""
        update_data = {
            "max_logs": 100,
            "auto_scroll": False,
            "filter_levels": [LogLevel.ERROR],
            "filter_source": "test_source"
        }
        
        self.component.update(update_data)
        
        self.assertEqual(self.component.max_logs, 100)
        self.assertFalse(self.component.auto_scroll)
        self.assertEqual(self.component.filter_levels, [LogLevel.ERROR])
        self.assertEqual(self.component.filter_source, "test_source")
    
    def test_get_log_count(self):
        """测试获取日志数量"""
        self.assertEqual(self.component.get_log_count(), 0)
        
        self.component.add_info("信息1")
        self.component.add_warning("警告")
        self.component.add_error("错误")
        
        self.assertEqual(self.component.get_log_count(), 3)
    
    def test_get_filtered_log_count(self):
        """测试获取过滤后的日志数量"""
        self.component.add_info("信息")
        self.component.add_warning("警告")
        self.component.add_error("错误")
        
        # 过滤错误日志
        self.component.set_filter_levels([LogLevel.ERROR])
        
        self.assertEqual(self.component.get_filtered_log_count(), 1)
    
    def test_get_logs_by_level(self):
        """测试按级别获取日志"""
        self.component.add_info("信息1")
        self.component.add_warning("警告")
        self.component.add_info("信息2")
        self.component.add_error("错误")
        
        info_logs = self.component.get_logs_by_level(LogLevel.INFO)
        self.assertEqual(len(info_logs), 2)
        self.assertEqual(info_logs[0].message, "信息1")
        self.assertEqual(info_logs[1].message, "信息2")
        
        error_logs = self.component.get_logs_by_level(LogLevel.ERROR)
        self.assertEqual(len(error_logs), 1)
        self.assertEqual(error_logs[0].message, "错误")
    
    def test_export_logs(self):
        """测试导出日志"""
        self.component.add_info("测试信息")
        self.component.add_error("测试错误")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        try:
            # 导出日志
            result = self.component.export_logs(temp_file)
            self.assertTrue(result)
            
            # 检查文件内容
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("测试信息", content)
                self.assertIn("测试错误", content)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_log_entry_timestamp(self):
        """测试日志条目时间戳"""
        import time
        
        log_entry = LogEntry(time.time(), LogLevel.INFO, "测试")
        timestamp_str = log_entry.get_timestamp_str()
        
        # 检查时间戳格式
        self.assertIsInstance(timestamp_str, str)
        self.assertIn(":", timestamp_str)
    
    def test_log_entry_icon(self):
        """测试日志条目图标"""
        log_entry = LogEntry(0, LogLevel.INFO, "测试")
        icon = log_entry.get_level_icon()
        
        # 检查图标
        self.assertIsInstance(icon, str)
        self.assertGreater(len(icon), 0)
    
    def test_size_constraints(self):
        """测试尺寸约束"""
        # 添加一些日志
        for i in range(10):
            self.component.add_info(f"这是一条很长的日志消息 {i}")
        
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
