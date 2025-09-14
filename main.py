import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input
from textual.screen import ModalScreen

# 导入日志系统和项目管理
from core.logging_system import setup_logging, get_logger
from core.project_manager import initialize_project_system, current_project_manager

# A-la-carte imports from existing TUI components
from tui_components.components.agent_status import AgentStatusComponent, AgentStatus
from tui_components.components.editor import EditorComponent
from tui_components.components.file_explorer import FileExplorerComponent
from tui_components.components.input_box import InputBoxComponent
from tui_components.components.log_panel import LogPanelComponent
from tui_components.components.menu_bar import MenuBarComponent, MenuGroup, MenuItem
from tui_components.components.project_selector import ProjectSelectorComponent, Project
from tui_components.components.status_panel import StatusPanelComponent


def get_project_list() -> list[Project]:
    """从项目管理器获取项目列表"""
    try:
        from core.project_manager import ProjectSelector
        selector = ProjectSelector()
        project_infos = selector.get_available_projects()
        
        projects = []
        for info in project_infos:
            projects.append(Project(name=info.name, path=info.path))
        
        return projects
    except Exception as e:
        # 如果获取失败，返回默认项目列表
        logger = get_logger(__name__)
        logger.error(f"获取项目列表失败: {e}")
        paths = ["/Users/xueyuheng/research/TeamDev/TeamDev/test_projects/测试项目_20250912_044108", "user-documents/测试项目2", "user-documents/测试项目3"]
        return [Project(name=p.split('/')[-1], path=p) for p in paths]

class ProjectSelectorScreen(ModalScreen[str]):
    """Screen to select a project."""
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+q", "cancel", "Cancel"),
        ("ctrl+p", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        projects = get_project_list()
        yield ProjectSelectorComponent(projects, id="project_selector")

    def on_project_selector_component_project_selected(self, event: ProjectSelectorComponent.ProjectSelected) -> None:
        self.dismiss(event.project.path)

    def action_cancel(self) -> None:
        """Dismiss the selector without selecting a project."""
        self.dismiss(None)

class TeamDevApp(App):
    """
    A Textual application for the TeamDev multi-agent collaboration system.
    """

    CSS = """
    Screen {
        layout: vertical;
    }
    #title {
        height: 3;
        content-align: left middle;
        padding: 0 1;
        background: $accent-darken-1;
    }
    #log_panel {
        height: 1fr;
        border: solid $accent-darken-2;
    }
    #input_box {
        height: 3;
        border: solid $accent;
        padding: 0 1;
    }
    #status_panel {
        height: 1;
        background: $accent-darken-3;
        color: $text;
        padding: 0 1;
    }
    """
    BINDINGS = [
        ("ctrl+t", "toggle_theme", "Toggle Theme"),
        ("ctrl+q", "quit_app", "Quit Application"),
    ]

    def __init__(self):
        super().__init__()
        # 顶部标题 + 中部对话日志 + 底部输入框 + 状态栏（终端界面风格）
        from textual.widgets import Static
        self.title_bar = Static("🔷 TeamDev — 本地多模型协作终端 (Ctrl+Q 退出)", id="title")
        self.log_panel = LogPanelComponent(id="log_panel")
        self.input_box = Input(placeholder="User: > ", id="input_box")
        self.status_panel = StatusPanelComponent(id="status_panel", default_message="TeamDev 就绪")

    def _setup_menu_bar(self) -> MenuBarComponent:
        file_menu = MenuGroup("File", [
            MenuItem("Select Project", "select_project", self.select_project),
            MenuItem("Save", "save_file", lambda: self.log_panel.add_info("Save action triggered.")),
            MenuItem("Quit", "quit", self.action_quit)
        ])
        edit_menu = MenuGroup("Edit", [
            MenuItem("Copy", "copy", lambda: self.log_panel.add_info("Copy action triggered.")),
            MenuItem("Paste", "paste", lambda: self.log_panel.add_info("Paste action triggered.")),
        ])
        help_menu = MenuGroup("Help", [
            MenuItem("About", "about", lambda: self.log_panel.add_info("TeamDev v0.1.0 - AI Collaboration Platform")),
        ])
        menu = MenuBarComponent(id="menu_bar")
        menu.add_menu_group(file_menu)
        menu.add_menu_group(edit_menu)
        menu.add_menu_group(help_menu)
        return menu

    def compose(self) -> ComposeResult:
        yield self.title_bar
        yield self.log_panel
        yield self.input_box
        yield self.status_panel

    def on_mount(self) -> None:
        self.log_panel.set_max_logs(500)
        self.log_panel.set_auto_scroll(True)
        
        # 检查是否已有当前项目
        current_project = current_project_manager.current_project
        if current_project:
            self.log_panel.add_info(f"当前项目: {current_project.name}", "system")
            self.log_panel.add_info(f"项目路径: {current_project.path}", "system")
        else:
            self.log_panel.add_info("欢迎使用 TeamDev 终端界面。", "system")
            self.log_panel.add_info("请先选择一个项目开始工作。", "system")
        
        self.log_panel.add_info("界面风格为终端交互界面。按 Ctrl+Q 退出，输入 /help 查看帮助。", "system")
        
        # 初始化状态栏
        self.status_panel.show_shortcuts()
        if current_project:
            self.status_panel.set_info(f"项目: {current_project.name} | 输入命令开始工作")
        else:
            self.status_panel.set_info("请选择项目 | 使用菜单或输入 /project 选择项目")
        
        # Set focus to the input box after mounting using a more reliable method
        self.set_focus(self.input_box)
    
    def focus_input_box(self) -> None:
        """Focus the input box after app is mounted"""
        # Try to focus on the input component
        try:
            self.input_box.focus()
        except Exception as e:
            # If direct focus fails, we'll rely on the component's natural behavior
            print(f"Could not directly set focus: {e}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理原生Input组件的提交事件"""
        text = event.value.strip()
        
        # 清空输入框
        event.input.clear()

        # 斜杠命令
        if text.startswith("/"):
            if text in ("/help", "/h"):
                self.log_panel.add_info("可用命令：", "help")
                self.log_panel.add_info("/help     显示帮助", "help")
                self.log_panel.add_info("/clear    清空对话", "help")
                self.log_panel.add_info("/project  选择项目", "help")
                self.log_panel.add_info("/switch   切换项目", "help")
                self.log_panel.add_info("/quit     退出程序（或直接 Ctrl+Q）", "help")
                self.status_panel.set_success("帮助信息已显示", auto_clear=True)
                return
            if text in ("/clear", "/cls"):
                self.log_panel.clear_logs()
                self.log_panel.add_info("已清空。", "system")
                self.status_panel.set_success("对话已清空", auto_clear=True)
                return
            if text in ("/project", "/p"):
                self.select_project()
                return
            if text in ("/switch", "/s"):
                self.switch_project()
                return
            if text in ("/quit", "/exit"):
                self.status_panel.set_info("正在退出...")
                self.exit(message="再见！")
                return

        # 普通回显（占位）
        if text:
            self.status_panel.show_busy("处理消息")
            self.log_panel.add_info(text, "user")
            await asyncio.sleep(0.2)
            self.log_panel.add_info("(占位回复) 我已收到你的消息。", "assistant")
            self.status_panel.show_ready()

    # 保留旧的事件处理方法以防兼容性问题
    async def on_input_box_component_submitted(self, event: InputBoxComponent.Submitted) -> None:
        """处理自定义InputBoxComponent的提交事件（兼容性保留）"""
        text = event.value.strip()
        
        # 直接处理，不需要调用 on_input_submitted
        if text.startswith("/"):
            if text in ("/help", "/h"):
                self.log_panel.add_info("可用命令：", "help")
                self.log_panel.add_info("/help     显示帮助", "help")
                self.log_panel.add_info("/clear    清空对话", "help")
                self.log_panel.add_info("/project  选择项目", "help")
                self.log_panel.add_info("/switch   切换项目", "help")
                self.log_panel.add_info("/quit     退出程序（或直接 Ctrl+Q）", "help")
                return
            elif text in ("/project", "/p"):
                self.select_project()
                return
            elif text in ("/switch", "/s"):
                self.switch_project()
                return
        
        # 普通消息处理
        if text:
            self.log_panel.add_info(text, "user")
            await asyncio.sleep(0.1)
            self.log_panel.add_info("(占位回复) 我已收到你的消息。", "assistant")

    def on_file_explorer_component_file_selected(self, event: FileExplorerComponent.FileSelected) -> None:
        """处理文件选择事件"""
        file_path = event.path
        self.log_panel.add_info(f"文件已选择: {file_path}", "fs")
        
        # 尝试读取文件内容并在日志中显示
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 只显示前几行作为预览
                lines = content.split('\n')[:5]
                preview = '\n'.join(lines)
                if len(lines) == 5:
                    preview += "\n..."
                self.log_panel.add_info(f"文件内容预览:\n{preview}", "fs")
        except Exception as e:
            self.log_panel.add_error(f"读取文件失败: {e}")

    def _handle_project_selected(self, project_path: Optional[str]) -> None:
        if project_path is None:
            self.log_panel.add_info("项目选择已取消", "system")
            return
            
        # 更新项目状态管理器
        try:
            from core.project_manager import ProjectSelector, ProjectInfo
            from datetime import datetime
            
            # 创建项目信息并设置为当前项目
            project_info = ProjectInfo(
                name=project_path.split('/')[-1],
                path=project_path,
                last_accessed=datetime.now()
            )
            current_project_manager.set_current_project(project_info)
            
            self.log_panel.add_info(f"已选择项目: {project_info.name}", "project")
            self.log_panel.add_info(f"项目路径: {project_path}", "project")
            self.status_panel.set_info(f"项目: {project_info.name} | 输入命令开始工作")
            
            logger = get_logger(__name__)
            logger.info(f"通过界面选择项目: {project_info.name}")
            
        except Exception as e:
            self.log_panel.add_error(f"设置项目失败: {e}")
            logger = get_logger(__name__)
            logger.error(f"设置项目失败: {e}")

    def select_project(self) -> None:
        self.push_screen(ProjectSelectorScreen(), self._handle_project_selected)
    
    def switch_project(self) -> None:
        """切换项目"""
        try:
            from core.project_manager import switch_project_interactive
            
            # 在后台执行项目切换
            self.log_panel.add_info("请在控制台中选择新项目...", "system")
            self.status_panel.set_info("正在切换项目，请查看控制台...")
            
            # 注意：这里只是通知用户，实际切换需要在控制台进行
            # 因为 TUI 环境下无法直接调用控制台交互
            self.log_panel.add_info("提示：切换项目需要重启应用或使用菜单", "system")
            
        except Exception as e:
            self.log_panel.add_error(f"切换项目失败: {e}")
            logger = get_logger(__name__)
            logger.error(f"切换项目失败: {e}")
        
    def action_toggle_theme(self) -> None:
        self.dark = not self.dark

    def action_quit_app(self) -> None:
        """Quit the application directly."""
        logger = get_logger(__name__)
        logger.info("用户退出应用")
        self.exit(message="再见！")

if __name__ == "__main__":
    # 初始化日志系统
    setup_logging(level='INFO', console_output=False)
    logger = get_logger(__name__)
    logger.info("TeamDev 应用启动")
    
    # 初始化项目系统
    if not initialize_project_system():
        print("未选择项目，程序退出")
        exit(0)
    
    # 启动 TUI 应用
    app = TeamDevApp()
    logger.info("启动 TUI 界面")
    app.run()