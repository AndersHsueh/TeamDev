"""
项目选择菜单组件
显示项目列表并提供选择功能
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style
from textual.message import Message
from textual import events


@dataclass
class Project:
    """项目信息"""
    name: str
    path: str
    description: str = ""
    language: str = ""
    last_modified: str = ""
    icon: str = "📁"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ProjectSelectorComponent(BaseComponent):
    """项目选择菜单组件"""

    class ProjectSelected(Message):
        """Posted when a project is selected."""
        def __init__(self, project: Project) -> None:
            self.project = project
            super().__init__()

    def __init__(self, projects: List[Project], *, id: str | None = None, classes: str | None = None, name: str | None = None):
        super().__init__(id=id, classes=classes, name=name)
        self.projects = projects
        self.selected_index = 0
        self.project_scroll_offset = 0
        self.search_text = ""
        self.filtered_projects: List[Project] = []
        self.show_description = True
        self.show_language = True
        self.show_last_modified = True
        self.show_tags = True
        self.group_by_language = False
        self.selected_color = get_color("selection")
        self.project_color = get_color("text")
        self.description_color = get_color("text_secondary")
        self.language_color = get_color("primary")
        self.tag_color = get_color("accent")
        self._update_filtered_projects()
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        # ProjectSelector组件暂时不需要特殊的更新逻辑
        pass

    def on_mount(self) -> None:
        self._update_filtered_projects()

    def set_search_text(self, text: str) -> None:
        self.search_text = text.lower()
        self._update_filtered_projects()
        self.selected_index = 0
        self.project_scroll_offset = 0
        self.refresh()

    def _update_filtered_projects(self) -> None:
        if not self.search_text:
            self.filtered_projects = self.projects.copy()
        else:
            self.filtered_projects = [
                p for p in self.projects 
                if self.search_text in f"{p.name} {p.description} {p.language} {' '.join(p.tags)}".lower()
            ]
        if self.selected_index >= len(self.filtered_projects):
            self.selected_index = max(0, len(self.filtered_projects) - 1)

    def render(self) -> str:
        lines = []
        max_height = self.size.height
        
        for i in range(self.project_scroll_offset, len(self.filtered_projects)):
            if len(lines) >= max_height:
                break
            
            project = self.filtered_projects[i]
            is_selected = (i == self.selected_index)
            
            project_lines = self._get_project_display_lines(project, self.size.width)
            
            for j, line in enumerate(project_lines):
                if is_selected and j == 0:
                    lines.append(f"[{self.selected_color}]{line}[/{self.selected_color}]")
                else:
                    lines.append(line)
        
        return "\n".join(lines)

    def _get_project_display_lines(self, project: Project, max_width: int) -> List[str]:
        lines = []
        main_line = f"{project.icon} {project.name}"
        if self.show_language and project.language:
            main_line += f" [{self.language_color}]{project.language}[/{self.language_color}]"
        lines.append(main_line)
        return lines

    def update(self, data: Any = None) -> None:
        pass

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if not self.filtered_projects:
            return

        if event.key in ("up", "k"):
            if self.selected_index > 0:
                self.selected_index -= 1
        elif event.key in ("down", "j"):
            if self.selected_index < len(self.filtered_projects) - 1:
                self.selected_index += 1
        elif event.key in ("enter", " "):
            project = self.filtered_projects[self.selected_index]
            self.post_message(self.ProjectSelected(project))
        
        self.refresh()