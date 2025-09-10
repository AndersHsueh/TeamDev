"""
菜单栏组件
支持顶部和底部菜单栏
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style


class MenuPosition(Enum):
    """菜单位置"""
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class MenuItem:
    """菜单项"""
    text: str
    key: str = ""
    action: Optional[Callable] = None
    enabled: bool = True
    visible: bool = True
    shortcut: str = ""
    icon: str = ""


@dataclass
class MenuGroup:
    """菜单组"""
    name: str
    items: List[MenuItem]
    separator: bool = False


class MenuBarComponent(BaseComponent):
    """菜单栏组件"""
    
    def __init__(self, name: str = "menu_bar", position: MenuPosition = MenuPosition.TOP):
        super().__init__(name)
        self.position = position
        self.menu_groups: List[MenuGroup] = []
        self.selected_group = -1
        self.selected_item = -1
        self.show_shortcuts = True
        self.show_icons = True
        self.compact_mode = False
        
        # 回调函数
        self.on_item_selected: Optional[Callable[[MenuItem], None]] = None
        self.on_shortcut_pressed: Optional[Callable[[str], None]] = None
        
        # 样式配置
        self.background_color = get_color("surface")
        self.text_color = get_color("text")
        self.selected_color = get_color("selection")
        self.disabled_color = get_color("text_muted")
        self.separator_color = get_color("border")
        self.shortcut_color = get_color("text_secondary")
    
    def add_menu_group(self, group: MenuGroup) -> None:
        """添加菜单组"""
        self.menu_groups.append(group)
    
    def add_menu_item(self, group_name: str, item: MenuItem) -> None:
        """向指定组添加菜单项"""
        for group in self.menu_groups:
            if group.name == group_name:
                group.items.append(item)
                return
        
        # 如果组不存在，创建新组
        new_group = MenuGroup(group_name, [item])
        self.add_menu_group(new_group)
    
    def remove_menu_group(self, group_name: str) -> None:
        """移除菜单组"""
        self.menu_groups = [g for g in self.menu_groups if g.name != group_name]
    
    def remove_menu_item(self, group_name: str, item_key: str) -> None:
        """移除菜单项"""
        for group in self.menu_groups:
            if group.name == group_name:
                group.items = [item for item in group.items if item.key != item_key]
                break
    
    def clear_menu(self) -> None:
        """清空菜单"""
        self.menu_groups.clear()
        self.selected_group = -1
        self.selected_item = -1
    
    def set_display_options(self, show_shortcuts: bool = True, show_icons: bool = True, 
                          compact_mode: bool = False) -> None:
        """设置显示选项"""
        self.show_shortcuts = show_shortcuts
        self.show_icons = show_icons
        self.compact_mode = compact_mode
    
    def _get_visible_groups(self) -> List[MenuGroup]:
        """获取可见的菜单组"""
        return [group for group in self.menu_groups if group.visible]
    
    def _get_visible_items(self, group: MenuGroup) -> List[MenuItem]:
        """获取可见的菜单项"""
        return [item for item in group.items if item.visible]
    
    def _render_menu_group(self, group: MenuGroup, start_x: int, max_width: int) -> str:
        """渲染菜单组"""
        if not group.items:
            return ""
        
        # 构建组标题
        group_text = group.name
        if self.show_icons and group.name.lower() in ["file", "edit", "view", "help"]:
            icons = {
                "file": "📁",
                "edit": "✏️",
                "view": "👁️",
                "help": "❓"
            }
            group_text = f"{icons.get(group.name.lower(), '')} {group.name}"
        
        # 应用样式
        if self.selected_group == self.menu_groups.index(group):
            group_text = f"[{self.selected_color}]{group_text}[/{self.selected_color}]"
        else:
            group_text = f"[{self.text_color}]{group_text}[/{self.text_color}]"
        
        return group_text
    
    def _render_menu_items(self, group: MenuGroup, start_x: int, max_width: int) -> List[str]:
        """渲染菜单项（下拉菜单）"""
        if not group.items:
            return []
        
        lines = []
        visible_items = self._get_visible_items(group)
        
        for i, item in enumerate(visible_items):
            if not item.visible:
                continue
            
            # 构建菜单项文本
            item_text = item.text
            
            # 添加图标
            if self.show_icons and item.icon:
                item_text = f"{item.icon} {item_text}"
            
            # 添加快捷键
            if self.show_shortcuts and item.shortcut:
                # 计算快捷键显示位置
                shortcut_text = f" {item.shortcut}"
                available_width = max_width - len(item_text) - len(shortcut_text)
                if available_width > 0:
                    item_text += " " * available_width + shortcut_text
            
            # 应用样式
            if not item.enabled:
                item_text = f"[{self.disabled_color}]{item_text}[/{self.disabled_color}]"
            elif self.selected_item == i:
                item_text = f"[{self.selected_color}]{item_text}[/{self.selected_color}]"
            else:
                item_text = f"[{self.text_color}]{item_text}[/{self.text_color}]"
            
            lines.append(item_text)
        
        return lines
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        if self.compact_mode:
            return self._render_compact()
        else:
            return self._render_full()
    
    def _render_compact(self) -> str:
        """渲染紧凑模式"""
        lines = []
        visible_groups = self._get_visible_groups()
        
        if not visible_groups:
            return "\n".join([""] * self.size.height)
        
        # 构建菜单行
        menu_parts = []
        current_x = 0
        
        for i, group in enumerate(visible_groups):
            group_text = group.name
            if self.show_icons and group.name.lower() in ["file", "edit", "view", "help"]:
                icons = {
                    "file": "📁",
                    "edit": "✏️",
                    "view": "👁️",
                    "help": "❓"
                }
                group_text = f"{icons.get(group.name.lower(), '')} {group.name}"
            
            # 应用选择样式
            if self.selected_group == i:
                group_text = f"[{self.selected_color}]{group_text}[/{self.selected_color}]"
            else:
                group_text = f"[{self.text_color}]{group_text}[/{self.text_color}]"
            
            menu_parts.append(group_text)
        
        menu_line = " | ".join(menu_parts)
        
        # 截断过长的菜单
        if len(menu_line) > self.size.width:
            menu_line = menu_line[:self.size.width-3] + "..."
        
        lines.append(menu_line)
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_full(self) -> str:
        """渲染完整模式"""
        lines = []
        visible_groups = self._get_visible_groups()
        
        if not visible_groups:
            return "\n".join([""] * self.size.height)
        
        # 构建菜单栏
        menu_parts = []
        current_x = 0
        
        for i, group in enumerate(visible_groups):
            group_text = self._render_menu_group(group, current_x, self.size.width - current_x)
            menu_parts.append(group_text)
            current_x += len(group.name) + 3  # +3 for spacing
        
        menu_line = " | ".join(menu_parts)
        
        # 截断过长的菜单
        if len(menu_line) > self.size.width:
            menu_line = menu_line[:self.size.width-3] + "..."
        
        lines.append(menu_line)
        
        # 如果选中了菜单组，显示下拉菜单
        if 0 <= self.selected_group < len(visible_groups):
            selected_group = visible_groups[self.selected_group]
            dropdown_lines = self._render_menu_items(selected_group, 0, self.size.width)
            
            # 限制下拉菜单高度
            max_dropdown_height = self.size.height - 1
            if len(dropdown_lines) > max_dropdown_height:
                dropdown_lines = dropdown_lines[:max_dropdown_height]
            
            lines.extend(dropdown_lines)
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "menu_groups" in data:
                self.menu_groups = data["menu_groups"]
            if "show_shortcuts" in data:
                self.show_shortcuts = data["show_shortcuts"]
            if "compact_mode" in data:
                self.compact_mode = data["compact_mode"]
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        if not self.visible:
            return False
        
        visible_groups = self._get_visible_groups()
        if not visible_groups:
            return False
        
        # 处理快捷键
        if self._handle_shortcut(key):
            return True
        
        # 处理菜单导航
        if key == "left" or key == "h":
            # 向左移动
            if self.selected_group > 0:
                self.selected_group -= 1
                self.selected_item = -1
            return True
        
        elif key == "right" or key == "l":
            # 向右移动
            if self.selected_group < len(visible_groups) - 1:
                self.selected_group += 1
                self.selected_item = -1
            return True
        
        elif key == "down" or key == "j":
            # 向下移动（在下拉菜单中）
            if 0 <= self.selected_group < len(visible_groups):
                group = visible_groups[self.selected_group]
                visible_items = self._get_visible_items(group)
                if self.selected_item < len(visible_items) - 1:
                    self.selected_item += 1
            return True
        
        elif key == "up" or key == "k":
            # 向上移动（在下拉菜单中）
            if self.selected_item > 0:
                self.selected_item -= 1
            return True
        
        elif key == "enter" or key == " ":
            # 选择菜单项
            if 0 <= self.selected_group < len(visible_groups):
                group = visible_groups[self.selected_group]
                visible_items = self._get_visible_items(group)
                if 0 <= self.selected_item < len(visible_items):
                    item = visible_items[self.selected_item]
                    if item.enabled and item.action:
                        item.action()
                    if self.on_item_selected:
                        self.on_item_selected(item)
            return True
        
        elif key == "escape":
            # 关闭菜单
            self.selected_group = -1
            self.selected_item = -1
            return True
        
        return False
    
    def _handle_shortcut(self, key: str) -> bool:
        """处理快捷键"""
        # 查找匹配的快捷键
        for group in self.menu_groups:
            for item in group.items:
                if item.shortcut and item.shortcut.lower() == key.lower():
                    if item.enabled and item.action:
                        item.action()
                    if self.on_shortcut_pressed:
                        self.on_shortcut_pressed(key)
                    return True
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        if not self.visible:
            return False
        
        visible_groups = self._get_visible_groups()
        if not visible_groups:
            return False
        
        # 计算点击的菜单组
        current_x = 0
        for i, group in enumerate(visible_groups):
            group_width = len(group.name) + 3  # +3 for spacing
            if current_x <= x < current_x + group_width:
                self.selected_group = i
                self.selected_item = -1
                
                if button == 1:  # 左键点击
                    # 可以在这里添加点击菜单组的逻辑
                    pass
                return True
            
            current_x += group_width
        
        # 处理下拉菜单中的点击
        if 0 <= self.selected_group < len(visible_groups) and y > 0:
            group = visible_groups[self.selected_group]
            visible_items = self._get_visible_items(group)
            
            item_index = y - 1  # -1 for menu bar
            if 0 <= item_index < len(visible_items):
                item = visible_items[item_index]
                if item.enabled and item.action:
                    item.action()
                if self.on_item_selected:
                    self.on_item_selected(item)
                return True
        
        return False
    
    def get_menu_item_by_shortcut(self, shortcut: str) -> Optional[MenuItem]:
        """根据快捷键获取菜单项"""
        for group in self.menu_groups:
            for item in group.items:
                if item.shortcut and item.shortcut.lower() == shortcut.lower():
                    return item
        return None
    
    def enable_menu_item(self, group_name: str, item_key: str, enabled: bool = True) -> None:
        """启用/禁用菜单项"""
        for group in self.menu_groups:
            if group.name == group_name:
                for item in group.items:
                    if item.key == item_key:
                        item.enabled = enabled
                        break
                break
    
    def set_menu_item_text(self, group_name: str, item_key: str, text: str) -> None:
        """设置菜单项文本"""
        for group in self.menu_groups:
            if group.name == group_name:
                for item in group.items:
                    if item.key == item_key:
                        item.text = text
                        break
                break
