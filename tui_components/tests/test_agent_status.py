"""
Agent 状态组件单元测试
"""

import unittest
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.agent_status import AgentStatusComponent, AgentStatus


class TestAgentStatusComponent(unittest.TestCase):
    """Agent 状态组件测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.component = AgentStatusComponent("test_agent")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.component.name, "test_agent")
        self.assertEqual(self.component.agent_name, "Agent")
        self.assertEqual(self.component.agent_avatar, "🤖")
        self.assertEqual(self.component.status, AgentStatus.IDLE)
        self.assertEqual(self.component.status_message, "")
        self.assertTrue(self.component.visible)
        self.assertFalse(self.component.focused)
    
    def test_set_agent_info(self):
        """测试设置 Agent 信息"""
        self.component.set_agent_info("Test Agent", "🧪")
        self.assertEqual(self.component.agent_name, "Test Agent")
        self.assertEqual(self.component.agent_avatar, "🧪")
    
    def test_set_status(self):
        """测试设置状态"""
        self.component.set_status(AgentStatus.WORKING, "处理中...")
        self.assertEqual(self.component.status, AgentStatus.WORKING)
        self.assertEqual(self.component.status_message, "处理中...")
    
    def test_set_display_options(self):
        """测试设置显示选项"""
        self.component.set_display_options(
            show_avatar=False,
            show_status_light=False,
            show_name=False,
            show_message=False
        )
        self.assertFalse(self.component.show_avatar)
        self.assertFalse(self.component.show_status_light)
        self.assertFalse(self.component.show_name)
        self.assertFalse(self.component.show_message)
    
    def test_render_basic(self):
        """测试基本渲染"""
        self.component.set_size(50, 3)
        rendered = self.component.render()
        
        # 检查渲染结果不为空
        self.assertIsInstance(rendered, str)
        self.assertGreater(len(rendered), 0)
        
        # 检查包含基本元素
        self.assertIn("🤖", rendered)  # 头像
        self.assertIn("Agent", rendered)  # 名称
    
    def test_render_with_status(self):
        """测试带状态的渲染"""
        self.component.set_agent_info("Test Agent", "🧪")
        self.component.set_status(AgentStatus.THINKING, "思考中...")
        self.component.set_size(50, 3)
        
        rendered = self.component.render()
        
        # 检查包含状态信息
        self.assertIn("Test Agent", rendered)
        self.assertIn("思考中...", rendered)
    
    def test_render_hidden_elements(self):
        """测试隐藏元素的渲染"""
        self.component.set_display_options(
            show_avatar=False,
            show_status_light=False,
            show_name=False,
            show_message=False
        )
        self.component.set_size(50, 3)
        
        rendered = self.component.render()
        
        # 检查不包含隐藏元素
        self.assertNotIn("🤖", rendered)
        self.assertNotIn("Agent", rendered)
    
    def test_update_with_dict(self):
        """测试使用字典更新"""
        update_data = {
            "name": "Updated Agent",
            "avatar": "🔄",
            "status": "working",
            "message": "更新中..."
        }
        
        self.component.update(update_data)
        
        self.assertEqual(self.component.agent_name, "Updated Agent")
        self.assertEqual(self.component.agent_avatar, "🔄")
        self.assertEqual(self.component.status, AgentStatus.WORKING)
        self.assertEqual(self.component.status_message, "更新中...")
    
    def test_update_with_invalid_status(self):
        """测试无效状态更新"""
        update_data = {
            "status": "invalid_status"
        }
        
        # 应该不会改变状态
        original_status = self.component.status
        self.component.update(update_data)
        self.assertEqual(self.component.status, original_status)
    
    def test_get_status_info(self):
        """测试获取状态信息"""
        self.component.set_agent_info("Test Agent", "🧪")
        self.component.set_status(AgentStatus.ERROR, "测试错误")
        
        status_info = self.component.get_status_info()
        
        self.assertIsInstance(status_info, dict)
        self.assertEqual(status_info["name"], "Test Agent")
        self.assertEqual(status_info["avatar"], "🧪")
        self.assertEqual(status_info["status"], "error")
        self.assertEqual(status_info["message"], "测试错误")
        self.assertIn("color", status_info)
        self.assertIn("icon", status_info)
    
    def test_handle_key(self):
        """测试键盘处理"""
        # Agent 状态组件通常不处理键盘输入
        result = self.component.handle_key("enter")
        self.assertFalse(result)
    
    def test_handle_mouse(self):
        """测试鼠标处理"""
        # Agent 状态组件通常不处理鼠标事件
        result = self.component.handle_mouse(10, 10, 1)
        self.assertFalse(result)
    
    def test_size_constraints(self):
        """测试尺寸约束"""
        self.component.set_size(10, 2)
        rendered = self.component.render()
        
        # 检查渲染结果不超过指定尺寸
        lines = rendered.split('\n')
        self.assertLessEqual(len(lines), 2)
        
        for line in lines:
            self.assertLessEqual(len(line), 10)
    
    def test_all_status_types(self):
        """测试所有状态类型"""
        statuses = [
            AgentStatus.IDLE,
            AgentStatus.THINKING,
            AgentStatus.WORKING,
            AgentStatus.ERROR,
            AgentStatus.OFFLINE
        ]
        
        for status in statuses:
            self.component.set_status(status, f"测试 {status.value}")
            self.component.set_size(50, 3)
            
            rendered = self.component.render()
            self.assertIsInstance(rendered, str)
            self.assertGreater(len(rendered), 0)
    
    def test_status_colors(self):
        """测试状态颜色"""
        # 检查状态颜色映射
        self.assertIn(AgentStatus.IDLE, self.component.status_colors)
        self.assertIn(AgentStatus.THINKING, self.component.status_colors)
        self.assertIn(AgentStatus.WORKING, self.component.status_colors)
        self.assertIn(AgentStatus.ERROR, self.component.status_colors)
        self.assertIn(AgentStatus.OFFLINE, self.component.status_colors)
    
    def test_status_icons(self):
        """测试状态图标"""
        # 检查状态图标映射
        self.assertIn(AgentStatus.IDLE, self.component.status_icons)
        self.assertIn(AgentStatus.THINKING, self.component.status_icons)
        self.assertIn(AgentStatus.WORKING, self.component.status_icons)
        self.assertIn(AgentStatus.ERROR, self.component.status_icons)
        self.assertIn(AgentStatus.OFFLINE, self.component.status_icons)


if __name__ == "__main__":
    unittest.main()
