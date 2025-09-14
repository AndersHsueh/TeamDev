#!/usr/bin/env python3
"""
简化的主程序测试版本
测试TUI组件的基本功能
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static

# 导入项目管理器
from core.project_manager import get_project_manager

def main():
    """简单的测试函数"""
    print("🚀 TeamDev 主程序测试")
    print("=" * 50)
    
    # 测试项目管理器
    print("📁 测试项目管理器...")
    try:
        pm = get_project_manager()
        projects = pm.list_projects()
        print(f"✅ 找到 {len(projects)} 个项目")
        for project in projects:
            print(f"  - {project['name']} ({project['id']})")
    except Exception as e:
        print(f"❌ 项目管理器测试失败: {e}")
    
    print("\n🧩 测试TUI组件导入...")
    try:
        from tui_components.components.agent_status import AgentStatusComponent, AgentStatus
        from tui_components.components.log_panel import LogPanelComponent
        from tui_components.components.menu_bar import MenuBarComponent, MenuGroup, MenuItem
        print("✅ TUI组件导入成功")
    except Exception as e:
        print(f"❌ TUI组件导入失败: {e}")
        return
    
    print("\n🎨 创建简单的Textual应用...")

class SimpleTestApp(App):
    """简单的测试应用"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #header {
        height: 3;
        background: $primary;
    }
    
    #content {
        height: 1fr;
        background: $surface;
    }
    
    #footer {
        height: 3;
        background: $primary;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Static("🚀 TeamDev 测试应用", id="header")
        yield Static("主内容区域\n\n按 Ctrl+C 退出", id="content")
        yield Static("状态栏 - 准备就绪", id="footer")
    
    def on_mount(self) -> None:
        self.title = "TeamDev Test App"

def run_textual_test():
    """运行Textual测试"""
    try:
        app = SimpleTestApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 用户退出应用")
    except Exception as e:
        print(f"❌ 应用运行失败: {e}")

if __name__ == "__main__":
    main()
    
    print("\n" + "=" * 50)
    print("🎮 启动Textual测试应用 (按 Ctrl+C 退出)")
    print("=" * 50)
    
    run_textual_test()
    
    print("\n✨ 测试完成!")
