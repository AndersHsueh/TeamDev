"""
项目选择菜单组件
显示项目列表并提供选择功能
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style


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
    
    def __init__(self, name: str = "project_selector"):
        super().__init__(name)
        self.projects: List[Project] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.search_text = ""
        self.filtered_projects: List[Project] = []
        self.show_description = True
        self.show_language = True
        self.show_last_modified = True
        self.show_tags = True
        self.group_by_language = False
        
        # 回调函数
        self.on_project_selected: Optional[Callable[[Project], None]] = None
        self.on_project_double_clicked: Optional[Callable[[Project], None]] = None
        
        # 样式配置
        self.selected_color = get_color("selection")
        self.project_color = get_color("text")
        self.description_color = get_color("text_secondary")
        self.language_color = get_color("primary")
        self.tag_color = get_color("accent")
        
        # 初始化过滤列表
        self._update_filtered_projects()
    
    def add_project(self, project: Project) -> None:
        """添加项目"""
        self.projects.append(project)
        self._update_filtered_projects()
    
    def remove_project(self, project: Project) -> None:
        """移除项目"""
        if project in self.projects:
            self.projects.remove(project)
            self._update_filtered_projects()
    
    def clear_projects(self) -> None:
        """清空项目列表"""
        self.projects.clear()
        self._update_filtered_projects()
    
    def set_projects(self, projects: List[Project]) -> None:
        """设置项目列表"""
        self.projects = projects.copy()
        self._update_filtered_projects()
    
    def set_search_text(self, text: str) -> None:
        """设置搜索文本"""
        self.search_text = text.lower()
        self._update_filtered_projects()
        self.selected_index = 0
        self.scroll_offset = 0
    
    def set_display_options(self, show_description: bool = True, show_language: bool = True,
                          show_last_modified: bool = True, show_tags: bool = True) -> None:
        """设置显示选项"""
        self.show_description = show_description
        self.show_language = show_language
        self.show_last_modified = show_last_modified
        self.show_tags = show_tags
    
    def set_group_by_language(self, group: bool) -> None:
        """设置是否按语言分组"""
        self.group_by_language = group
        self._update_filtered_projects()
    
    def _update_filtered_projects(self) -> None:
        """更新过滤后的项目列表"""
        if not self.search_text:
            self.filtered_projects = self.projects.copy()
        else:
            self.filtered_projects = []
            for project in self.projects:
                # 搜索项目名称、描述、语言和标签
                searchable_text = f"{project.name} {project.description} {project.language} {' '.join(project.tags)}".lower()
                if self.search_text in searchable_text:
                    self.filtered_projects.append(project)
        
        # 按语言分组
        if self.group_by_language:
            self._group_projects_by_language()
        
        # 确保选中索引有效
        if self.selected_index >= len(self.filtered_projects):
            self.selected_index = max(0, len(self.filtered_projects) - 1)
    
    def _group_projects_by_language(self) -> None:
        """按语言分组项目"""
        language_groups = {}
        for project in self.filtered_projects:
            lang = project.language or "Other"
            if lang not in language_groups:
                language_groups[lang] = []
            language_groups[lang].append(project)
        
        # 重新组织列表
        grouped_projects = []
        for lang in sorted(language_groups.keys()):
            grouped_projects.extend(language_groups[lang])
        
        self.filtered_projects = grouped_projects
    
    def _get_project_display_lines(self, project: Project, max_width: int) -> List[str]:
        """获取项目的显示行"""
        lines = []
        
        # 主行：图标 + 名称
        main_line = f"{project.icon} {project.name}"
        if self.show_language and project.language:
            main_line += f" [{self.language_color}]{project.language}[/{self.language_color}]"
        lines.append(main_line)
        
        # 描述行
        if self.show_description and project.description:
            desc_line = f"    {project.description}"
            if len(desc_line) > max_width:
                desc_line = desc_line[:max_width-3] + "..."
            lines.append(f"[{self.description_color}]{desc_line}[/{self.description_color}]")
        
        # 标签行
        if self.show_tags and project.tags:
            tags_text = " ".join([f"[{self.tag_color}]{tag}[/{self.tag_color}]" for tag in project.tags])
            tags_line = f"    Tags: {tags_text}"
            if len(tags_line) > max_width:
                tags_line = tags_line[:max_width-3] + "..."
            lines.append(tags_line)
        
        # 最后修改时间行
        if self.show_last_modified and project.last_modified:
            time_line = f"    Last modified: {project.last_modified}"
            if len(time_line) > max_width:
                time_line = time_line[:max_width-3] + "..."
            lines.append(f"[{self.description_color}]{time_line}[/{self.description_color}]")
        
        return lines
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        lines = []
        max_width = self.size.width
        max_height = self.size.height
        
        # 显示搜索框（如果有搜索文本）
        if self.search_text:
            search_line = f"🔍 {self.search_text}"
            if len(search_line) > max_width:
                search_line = search_line[:max_width-3] + "..."
            lines.append(f"[{get_color('info')}]{search_line}[/{get_color('info')}]")
            max_height -= 1
        
        # 显示项目列表
        current_line = 0
        start_idx = self.scroll_offset
        
        for i in range(start_idx, len(self.filtered_projects)):
            if current_line >= max_height:
                break
            
            project = self.filtered_projects[i]
            is_selected = (i == self.selected_index)
            
            # 获取项目显示行
            project_lines = self._get_project_display_lines(project, max_width)
            
            for j, line in enumerate(project_lines):
                if current_line >= max_height:
                    break
                
                # 应用选择高亮
                if is_selected and j == 0:  # 只高亮主行
                    line = f"[{self.selected_color}]{line}[/{self.selected_color}]"
                
                lines.append(line)
                current_line += 1
            
            # 项目间添加空行
            if i < len(self.filtered_projects) - 1:
                lines.append("")
                current_line += 1
        
        # 显示统计信息
        if current_line < max_height:
            stats_line = f"Showing {len(self.filtered_projects)} of {len(self.projects)} projects"
            if len(stats_line) > max_width:
                stats_line = stats_line[:max_width-3] + "..."
            lines.append(f"[{get_color('text_muted')}]{stats_line}[/{get_color('text_muted')}]")
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "projects" in data:
                self.set_projects(data["projects"])
            if "search_text" in data:
                self.set_search_text(data["search_text"])
            if "group_by_language" in data:
                self.set_group_by_language(data["group_by_language"])
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        if not self.visible:
            return False
        
        if not self.filtered_projects:
            return False
        
        if key == "up" or key == "k":
            # 向上移动
            if self.selected_index > 0:
                self.selected_index -= 1
                self._ensure_selected_visible()
            return True
        
        elif key == "down" or key == "j":
            # 向下移动
            if self.selected_index < len(self.filtered_projects) - 1:
                self.selected_index += 1
                self._ensure_selected_visible()
            return True
        
        elif key == "page_up" or key == "ctrl+u":
            # 向上翻页
            page_size = self.size.height // 2
            self.selected_index = max(0, self.selected_index - page_size)
            self._ensure_selected_visible()
            return True
        
        elif key == "page_down" or key == "ctrl+d":
            # 向下翻页
            page_size = self.size.height // 2
            self.selected_index = min(len(self.filtered_projects) - 1, self.selected_index + page_size)
            self._ensure_selected_visible()
            return True
        
        elif key == "home" or key == "g":
            # 移动到顶部
            self.selected_index = 0
            self.scroll_offset = 0
            return True
        
        elif key == "end" or key == "G":
            # 移动到底部
            self.selected_index = len(self.filtered_projects) - 1
            self._ensure_selected_visible()
            return True
        
        elif key == "enter" or key == " ":
            # 选择项目
            if 0 <= self.selected_index < len(self.filtered_projects):
                project = self.filtered_projects[self.selected_index]
                if self.on_project_selected:
                    self.on_project_selected(project)
            return True
        
        elif key == "ctrl+f":
            # 开始搜索（这里应该触发搜索对话框）
            pass
        
        elif key == "escape":
            # 清除搜索
            self.set_search_text("")
            return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        if not self.visible:
            return False
        
        # 计算点击的项目索引
        # 这里需要更复杂的逻辑来计算点击的项目，因为每个项目可能占用多行
        # 简化实现：假设每个项目占用固定行数
        lines_per_project = 2  # 简化：每个项目占用2行
        search_offset = 1 if self.search_text else 0  # 搜索框占用1行
        
        click_y = y - search_offset
        if click_y < 0:
            return False
        
        project_index = self.scroll_offset + click_y // lines_per_project
        
        if 0 <= project_index < len(self.filtered_projects):
            self.selected_index = project_index
            
            if button == 1:  # 左键单击
                project = self.filtered_projects[project_index]
                if self.on_project_selected:
                    self.on_project_selected(project)
            elif button == 2:  # 双击
                project = self.filtered_projects[project_index]
                if self.on_project_double_clicked:
                    self.on_project_double_clicked(project)
            
            return True
        
        return False
    
    def _ensure_selected_visible(self) -> None:
        """确保选中的项目可见"""
        if not self.filtered_projects:
            return
        
        # 计算每个项目占用的行数（简化）
        lines_per_project = 2
        visible_projects = self.size.height // lines_per_project
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_projects:
            self.scroll_offset = self.selected_index - visible_projects + 1
    
    def get_selected_project(self) -> Optional[Project]:
        """获取当前选中的项目"""
        if 0 <= self.selected_index < len(self.filtered_projects):
            return self.filtered_projects[self.selected_index]
        return None
    
    def get_projects_by_language(self, language: str) -> List[Project]:
        """获取指定语言的项目"""
        return [p for p in self.projects if p.language == language]
    
    def get_projects_by_tag(self, tag: str) -> List[Project]:
        """获取包含指定标签的项目"""
        return [p for p in self.projects if tag in p.tags]
    
    def export_projects_list(self) -> List[Dict[str, Any]]:
        """导出项目列表"""
        return [
            {
                "name": p.name,
                "path": p.path,
                "description": p.description,
                "language": p.language,
                "last_modified": p.last_modified,
                "tags": p.tags
            }
            for p in self.projects
        ]
