import asyncio
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.screen import ModalScreen

# A-la-carte imports from existing TUI components
from tui_components.components.agent_status import AgentStatusComponent, AgentStatus
from tui_components.components.editor import EditorComponent
from tui_components.components.file_explorer import FileExplorerComponent
from tui_components.components.input_box import InputBoxComponent
from tui_components.components.log_panel import LogPanelComponent
from tui_components.components.menu_bar import MenuBarComponent, MenuGroup, MenuItem
from tui_components.components.project_selector import ProjectSelectorComponent, Project

def get_project_list() -> list[Project]:
    """Placeholder for project manager API."""
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
        border-top: solid $accent;
    }
    """
    BINDINGS = [
        ("ctrl+t", "toggle_theme", "Toggle Theme"),
    ]

    def __init__(self):
        super().__init__()
        # 顶部标题 + 中部对话日志 + 底部输入框（gemini-cli 风格）
        from textual.widgets import Static
        self.title_bar = Static("🔷 TeamDev — 本地多模型协作终端 (Ctrl+C 退出，输入 /help)", id="title")
        self.log_panel = LogPanelComponent(id="log_panel")
        self.input_box = InputBoxComponent(id="input_box", placeholder="gemini> ")

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

    def on_mount(self) -> None:
        self.log_panel.set_max_logs(500)
        self.log_panel.set_auto_scroll(True)
        self.log_panel.add_info("欢迎使用 TeamDev 终端界面。", "system")
        self.log_panel.add_info("界面风格参考 gemini-cli。按 Ctrl+C 退出，输入 /help 查看帮助。", "system")

    async def on_input_box_component_submitted(self, event: InputBoxComponent.Submitted) -> None:
        text = event.value.strip()

        # 斜杠命令
        if text.startswith("/"):
            if text in ("/help", "/h"):
                self.log_panel.add_info("可用命令：/help, /clear, /quit", "help")
                self.log_panel.add_info("/help  显示帮助", "help")
                self.log_panel.add_info("/clear 清空对话", "help")
                self.log_panel.add_info("/quit  退出程序（或直接 Ctrl+C）", "help")
                return
            if text in ("/clear", "/cls"):
                self.log_panel.clear_logs()
                self.log_panel.add_info("已清空。", "system")
                return
            if text in ("/quit", "/exit"):
                self.exit(message="再见！")
                return

        # 普通回显（占位）
        if text:
            self.log_panel.add_info(text, "user")
            await asyncio.sleep(0.2)
            self.log_panel.add_info("(占位回复) 我已收到你的消息。", "assistant")

    def on_file_explorer_component_file_selected(self, event: FileExplorerComponent.FileSelected) -> None:
        file_path = event.path
        self.log_panel.add_info(f"File selected: {file_path}", "fs")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.editor.set_text(f.read())
        except Exception as e:
            self.log_panel.add_error(f"Failed to read file: {e}")
            self.editor.set_text(f"# Error opening file\n\n{e}")

    def _handle_project_selected(self, project_path: str) -> None:
        self.current_project_path = project_path
        self.log_panel.add_info(f"Project '{project_path}' selected.", "project")
        self.file_explorer.set_root_path(project_path)
        self.agent_status.set_status(AgentStatus.IDLE, "Project loaded. Ready for commands.")
        self.editor.set_text(f"# Project Loaded\n\nPath: {project_path}\n\nSelect a file to view its contents.")

    def select_project(self) -> None:
        self.push_screen(ProjectSelectorScreen(), self._handle_project_selected)
        
    def action_toggle_theme(self) -> None:
        self.dark = not self.dark

if __name__ == "__main__":
    app = TeamDevApp()
    app.run()