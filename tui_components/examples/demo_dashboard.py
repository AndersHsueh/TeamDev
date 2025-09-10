"""
演示完整界面
展示文件树 + 编辑器 + Agent 状态 + 日志的完整布局
"""

import sys
import os
import time
from typing import Dict, Any

# 添加父目录到路径，以便导入组件
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_component import BaseComponent
from core.layout_manager import LayoutManager, LayoutType, Alignment
from core.theme import set_theme, Themes
from components.agent_status import AgentStatusComponent, AgentStatus
from components.file_explorer import FileExplorerComponent
from components.log_panel import LogPanelComponent, LogLevel
from components.editor import EditorComponent
from components.menu_bar import MenuBarComponent, MenuGroup, MenuItem, MenuPosition


class DashboardApp(BaseComponent):
    """仪表板应用程序"""
    
    def __init__(self):
        super().__init__("dashboard")
        
        # 设置主题
        set_theme(Themes.get_dark_theme())
        
        # 创建布局管理器
        self.layout_manager = LayoutManager()
        self.layout_manager.set_layout_type(LayoutType.VERTICAL)
        self.layout_manager.set_spacing(1)
        
        # 创建组件
        self._create_components()
        
        # 设置初始布局
        self._setup_layout()
        
        # 模拟数据
        self._setup_demo_data()
    
    def _create_components(self):
        """创建所有组件"""
        # 菜单栏
        self.menu_bar = MenuBarComponent("main_menu", MenuPosition.TOP)
        self._setup_menu_bar()
        
        # 主内容区域
        self.main_content = BaseComponent("main_content")
        
        # 文件浏览器
        self.file_explorer = FileExplorerComponent("file_explorer")
        self.file_explorer.set_root_path(".")
        self.file_explorer.set_file_select_callback(self._on_file_selected)
        
        # 编辑器
        self.editor = EditorComponent("editor")
        self.editor.set_text("# 欢迎使用 TUI 组件库演示\n\n这是一个完整的仪表板示例，展示了以下组件：\n\n1. 文件浏览器 - 左侧显示文件树\n2. 代码编辑器 - 中间显示文件内容\n3. Agent 状态 - 右上角显示 AI 助手状态\n4. 日志面板 - 右下角显示系统日志\n5. 菜单栏 - 顶部显示操作菜单\n\n使用方向键导航，Enter 键选择，Ctrl+Q 退出。")
        
        # Agent 状态
        self.agent_status = AgentStatusComponent("agent_status")
        self.agent_status.set_agent_info("Claude", "🤖")
        self.agent_status.set_status(AgentStatus.THINKING, "正在分析代码...")
        
        # 日志面板
        self.log_panel = LogPanelComponent("log_panel")
        self.log_panel.set_max_logs(100)
        self.log_panel.set_auto_scroll(True)
        
        # 添加组件到主内容区域
        self.main_content.add_child(self.file_explorer)
        self.main_content.add_child(self.editor)
        self.main_content.add_child(self.agent_status)
        self.main_content.add_child(self.log_panel)
        
        # 添加组件到根容器
        self.add_child(self.menu_bar)
        self.add_child(self.main_content)
    
    def _setup_menu_bar(self):
        """设置菜单栏"""
        # 文件菜单
        file_menu = MenuGroup("File", [
            MenuItem("New", "new", self._menu_new_file, shortcut="Ctrl+N"),
            MenuItem("Open", "open", self._menu_open_file, shortcut="Ctrl+O"),
            MenuItem("Save", "save", self._menu_save_file, shortcut="Ctrl+S"),
            MenuItem("Save As", "save_as", self._menu_save_as_file, shortcut="Ctrl+Shift+S"),
            MenuItem("Exit", "exit", self._menu_exit, shortcut="Ctrl+Q"),
        ])
        
        # 编辑菜单
        edit_menu = MenuGroup("Edit", [
            MenuItem("Undo", "undo", self._menu_undo, shortcut="Ctrl+Z"),
            MenuItem("Redo", "redo", self._menu_redo, shortcut="Ctrl+Y"),
            MenuItem("Cut", "cut", self._menu_cut, shortcut="Ctrl+X"),
            MenuItem("Copy", "copy", self._menu_copy, shortcut="Ctrl+C"),
            MenuItem("Paste", "paste", self._menu_paste, shortcut="Ctrl+V"),
            MenuItem("Find", "find", self._menu_find, shortcut="Ctrl+F"),
        ])
        
        # 视图菜单
        view_menu = MenuGroup("View", [
            MenuItem("File Explorer", "toggle_file_explorer", self._menu_toggle_file_explorer, shortcut="F1"),
            MenuItem("Log Panel", "toggle_log_panel", self._menu_toggle_log_panel, shortcut="F2"),
            MenuItem("Agent Status", "toggle_agent_status", self._menu_toggle_agent_status, shortcut="F3"),
        ])
        
        # 帮助菜单
        help_menu = MenuGroup("Help", [
            MenuItem("About", "about", self._menu_about),
            MenuItem("Shortcuts", "shortcuts", self._menu_shortcuts),
        ])
        
        self.menu_bar.add_menu_group(file_menu)
        self.menu_bar.add_menu_group(edit_menu)
        self.menu_bar.add_menu_group(view_menu)
        self.menu_bar.add_menu_group(help_menu)
    
    def _setup_layout(self):
        """设置布局"""
        # 设置组件尺寸
        self.menu_bar.set_size(self.size.width, 1)
        self.main_content.set_size(self.size.width, self.size.height - 1)
        
        # 主内容区域使用水平布局
        main_layout = LayoutManager()
        main_layout.set_layout_type(LayoutType.HORIZONTAL)
        main_layout.set_spacing(1)
        
        # 左侧：文件浏览器 (25%)
        file_width = int(self.size.width * 0.25)
        self.file_explorer.set_size(file_width, self.size.height - 1)
        
        # 右侧：编辑器区域 (75%)
        editor_width = self.size.width - file_width - 1
        editor_height = self.size.height - 1
        
        # 编辑器区域使用垂直布局
        editor_layout = LayoutManager()
        editor_layout.set_layout_type(LayoutType.VERTICAL)
        editor_layout.set_spacing(1)
        
        # 顶部：编辑器 (70%)
        editor_content_height = int(editor_height * 0.7)
        self.editor.set_size(editor_width, editor_content_height)
        
        # 底部：状态和日志区域 (30%)
        status_height = editor_height - editor_content_height - 1
        
        # 状态区域使用水平布局
        status_layout = LayoutManager()
        status_layout.set_layout_type(LayoutType.HORIZONTAL)
        status_layout.set_spacing(1)
        
        # Agent 状态 (30%)
        agent_width = int(editor_width * 0.3)
        self.agent_status.set_size(agent_width, status_height)
        
        # 日志面板 (70%)
        log_width = editor_width - agent_width - 1
        self.log_panel.set_size(log_width, status_height)
    
    def _setup_demo_data(self):
        """设置演示数据"""
        # 添加一些示例日志
        self.log_panel.add_info("应用程序启动", "system")
        self.log_panel.add_info("加载文件浏览器", "file_explorer")
        self.log_panel.add_info("初始化编辑器", "editor")
        self.log_panel.add_info("连接 AI 助手", "agent")
        self.log_panel.add_warning("某些功能可能需要网络连接", "system")
        self.log_panel.add_info("仪表板准备就绪", "system")
        
        # 模拟 Agent 状态变化
        self._simulate_agent_activity()
    
    def _simulate_agent_activity(self):
        """模拟 Agent 活动"""
        import threading
        
        def agent_worker():
            while True:
                time.sleep(3)
                self.agent_status.set_status(AgentStatus.THINKING, "分析代码结构...")
                self.log_panel.add_info("Agent 开始分析代码", "agent")
                
                time.sleep(2)
                self.agent_status.set_status(AgentStatus.WORKING, "生成建议...")
                self.log_panel.add_info("Agent 正在生成代码建议", "agent")
                
                time.sleep(2)
                self.agent_status.set_status(AgentStatus.IDLE, "等待指令")
                self.log_panel.add_info("Agent 分析完成", "agent")
        
        # 在后台线程中运行
        agent_thread = threading.Thread(target=agent_worker, daemon=True)
        agent_thread.start()
    
    def _on_file_selected(self, file_path: str):
        """文件选择回调"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.editor.set_text(content)
                self.log_panel.add_info(f"打开文件: {file_path}", "file_explorer")
        except Exception as e:
            self.log_panel.add_error(f"无法打开文件 {file_path}: {str(e)}", "file_explorer")
    
    # 菜单回调函数
    def _menu_new_file(self):
        self.editor.set_text("")
        self.log_panel.add_info("创建新文件", "menu")
    
    def _menu_open_file(self):
        self.log_panel.add_info("打开文件对话框", "menu")
    
    def _menu_save_file(self):
        self.log_panel.add_info("保存文件", "menu")
    
    def _menu_save_as_file(self):
        self.log_panel.add_info("另存为文件", "menu")
    
    def _menu_exit(self):
        self.log_panel.add_info("退出应用程序", "menu")
        sys.exit(0)
    
    def _menu_undo(self):
        self.log_panel.add_info("撤销操作", "menu")
    
    def _menu_redo(self):
        self.log_panel.add_info("重做操作", "menu")
    
    def _menu_cut(self):
        self.log_panel.add_info("剪切文本", "menu")
    
    def _menu_copy(self):
        self.log_panel.add_info("复制文本", "menu")
    
    def _menu_paste(self):
        self.log_panel.add_info("粘贴文本", "menu")
    
    def _menu_find(self):
        self.log_panel.add_info("查找文本", "menu")
    
    def _menu_toggle_file_explorer(self):
        self.file_explorer.set_visible(not self.file_explorer.visible)
        self.log_panel.add_info(f"文件浏览器: {'显示' if self.file_explorer.visible else '隐藏'}", "menu")
    
    def _menu_toggle_log_panel(self):
        self.log_panel.set_visible(not self.log_panel.visible)
        self.log_panel.add_info(f"日志面板: {'显示' if self.log_panel.visible else '隐藏'}", "menu")
    
    def _menu_toggle_agent_status(self):
        self.agent_status.set_visible(not self.agent_status.visible)
        self.log_panel.add_info(f"Agent 状态: {'显示' if self.agent_status.visible else '隐藏'}", "menu")
    
    def _menu_about(self):
        self.log_panel.add_info("TUI 组件库演示 v1.0", "menu")
    
    def _menu_shortcuts(self):
        self.log_panel.add_info("快捷键帮助: Ctrl+Q 退出, F1-F3 切换面板", "menu")
    
    def render(self) -> str:
        """渲染整个应用程序"""
        if not self.visible:
            return ""
        
        # 更新布局
        self._setup_layout()
        
        # 渲染所有组件
        lines = []
        
        # 菜单栏
        menu_lines = self.menu_bar.render().split('\n')
        lines.extend(menu_lines)
        
        # 主内容区域
        main_lines = self.main_content.render().split('\n')
        lines.extend(main_lines)
        
        return '\n'.join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新应用程序状态"""
        # 更新所有子组件
        for child in self.children:
            child.update(data)
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        # 处理全局快捷键
        if key == "ctrl+q":
            self._menu_exit()
            return True
        
        # 处理菜单栏快捷键
        if self.menu_bar.handle_key(key):
            return True
        
        # 处理其他组件的键盘输入
        for child in self.children:
            if child.handle_key(key):
                return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        # 处理所有组件的鼠标事件
        for child in self.children:
            if child.handle_mouse(x, y, button):
                return True
        
        return False


def main():
    """主函数"""
    print("启动 TUI 组件库演示...")
    print("使用 Ctrl+Q 退出程序")
    print("=" * 50)
    
    # 创建应用程序
    app = DashboardApp()
    app.set_size(120, 30)  # 设置窗口大小
    app.set_visible(True)
    
    # 模拟主循环
    try:
        while True:
            # 清屏
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # 渲染应用程序
            print(app.render())
            
            # 获取用户输入
            try:
                import tty
                import termios
                
                # 设置终端为原始模式
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                
                # 读取一个字符
                key = sys.stdin.read(1)
                
                # 处理特殊键
                if key == '\x03':  # Ctrl+C
                    break
                elif key == '\x11':  # Ctrl+Q
                    app._menu_exit()
                    break
                elif key == '\x0c':  # Ctrl+L
                    continue  # 刷新屏幕
                
                # 恢复终端设置
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                
                # 处理键盘输入
                app.handle_key(key)
                
            except ImportError:
                # 如果没有 termios 模块，使用简单的输入
                user_input = input("\n按 Enter 继续，输入 'q' 退出: ")
                if user_input.lower() == 'q':
                    break
                app.handle_key('enter')
            
            # 更新应用程序
            app.update()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {e}")
    finally:
        print("程序结束")


if __name__ == "__main__":
    main()
