"""
文件浏览树组件
显示文件系统目录结构
"""

import os
from typing import List, Dict, Any, Optional, Callable
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style
from textual.message import Message
from textual import events


class FileNode:
    """文件节点"""
    
    def __init__(self, path: str, name: str = "", is_dir: bool = False):
        self.path = path
        self.name = name or os.path.basename(path)
        self.is_dir = is_dir
        self.expanded = False
        self.children: List['FileNode'] = []
        self.parent: Optional['FileNode'] = None
        self.selected = False
    
    def add_child(self, child: 'FileNode') -> None:
        """添加子节点"""
        child.parent = self
        self.children.append(child)
    
    def get_icon(self) -> str:
        """获取文件图标"""
        if self.is_dir:
            return "📁" if self.expanded else "📂"
        else:
            ext = os.path.splitext(self.name)[1].lower()
            icon_map = {
                '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
                '.json': '📋', '.md': '📝', '.txt': '📄', '.png': '🖼️',
                '.jpg': '🖼️', '.gif': '🖼️', '.zip': '📦', '.pdf': '📕',
            }
            return icon_map.get(ext, '📄')
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return f"{self.get_icon()} {self.name}"


class FileExplorerComponent(BaseComponent):
    """文件浏览树组件"""

    class FileSelected(Message):
        """Posted when a file is selected."""
        def __init__(self, path: str) -> None:
            self.path = path
            super().__init__()

    def __init__(self, *, id: Optional[str] = None, classes: Optional[str] = None, name: Optional[str] = None):
        super().__init__(id=id, classes=classes, name=name)
        self.root_path = "."
        self.root_node: Optional[FileNode] = None
        self.current_node: Optional[FileNode] = None
        self.file_scroll_offset = 0
        self.hidden_files = True
        self.file_filter: Optional[Callable[[str], bool]] = None
        self.indent_size = 2
        self.selected_color = get_color("selection")
        self.directory_color = get_color("primary")
        self.file_color = get_color("text")
        self.hidden_color = get_color("text_muted")

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.set_root_path(self.root_path)

    def set_root_path(self, path: str) -> None:
        """设置根路径"""
        self.root_path = path
        self._build_tree()
        self.refresh()

    def _build_tree(self) -> None:
        """构建文件树"""
        if not os.path.exists(self.root_path):
            self.root_node = None
            return
        
        self.root_node = FileNode(self.root_path, os.path.basename(self.root_path), True)
        self._build_node_children(self.root_node)
        self.current_node = self.root_node
        if self.current_node:
            self.current_node.selected = True

    def _build_node_children(self, node: FileNode) -> None:
        """构建节点的子节点"""
        if not node.is_dir:
            return
        
        try:
            items = sorted(os.listdir(node.path), key=lambda x: (not os.path.isdir(os.path.join(node.path, x)), x.lower()))
            for item in items:
                item_path = os.path.join(node.path, item)
                if not self.hidden_files and item.startswith('.'):
                    continue
                if self.file_filter and not self.file_filter(item_path):
                    continue
                
                is_dir = os.path.isdir(item_path)
                child_node = FileNode(item_path, item, is_dir)
                node.add_child(child_node)
        except PermissionError:
            pass

    def _get_visible_nodes(self) -> List[FileNode]:
        """获取可见的节点列表（扁平化）"""
        if not self.root_node:
            return []
        
        visible_nodes = []
        self._flatten_nodes(self.root_node, visible_nodes)
        return visible_nodes

    def _flatten_nodes(self, node: FileNode, result: List[FileNode]) -> None:
        """扁平化节点树"""
        result.append(node)
        if node.is_dir and node.expanded:
            for child in node.children:
                self._flatten_nodes(child, result)

    def render(self) -> str:
        """渲染组件内容"""
        lines = []
        visible_nodes = self._get_visible_nodes()
        
        start_idx = self.file_scroll_offset
        end_idx = min(start_idx + self.size.height, len(visible_nodes))
        
        for i in range(start_idx, end_idx):
            node = visible_nodes[i]
            level = self._get_node_level(node)
            indent = " " * (level * self.indent_size)
            display_name = node.get_display_name()
            
            if node.selected:
                color = self.selected_color
            elif node.is_dir:
                color = self.directory_color
            else:
                color = self.file_color
            
            line = f"{indent}{display_name}"
            lines.append(f"[{color}]{line}[/{color}]")
        
        return "\n".join(lines)

    def _get_node_level(self, node: FileNode) -> int:
        """获取节点层级"""
        level = 0
        current = node
        while current.parent:
            level += 1
            current = current.parent
        return level
    
    def update(self, data: Any = None) -> None:
        if isinstance(data, dict):
            if "root_path" in data:
                self.set_root_path(data["root_path"])

    def on_key(self, event: events.Key) -> None:
        """处理键盘输入"""
        event.stop()
        visible_nodes = self._get_visible_nodes()
        if not visible_nodes:
            return

        current_index = self._get_current_node_index()
        if current_index == -1:
            current_index = 0

        if event.key in ("up", "k"):
            if current_index > 0:
                self._select_node_at_index(current_index - 1)
        elif event.key in ("down", "j"):
            if current_index < len(visible_nodes) - 1:
                self._select_node_at_index(current_index + 1)
        elif event.key in ("enter", " "):
            node = visible_nodes[current_index]
            if node.is_dir:
                node.expanded = not node.expanded
            else:
                self.post_message(self.FileSelected(node.path))
        elif event.key in ("left", "h"):
            node = visible_nodes[current_index]
            if node.is_dir and node.expanded:
                node.expanded = False
            elif node.parent:
                self._select_node(node.parent)
        elif event.key in ("right", "l"):
            node = visible_nodes[current_index]
            if node.is_dir:
                node.expanded = True
        
        self.refresh()

    def _get_current_node_index(self) -> int:
        """获取当前选中节点的索引"""
        return next((i for i, node in enumerate(self._get_visible_nodes()) if node.selected), -1)

    def _select_node(self, new_node: FileNode) -> None:
        """选择一个新节点"""
        for node in self._get_visible_nodes():
            node.selected = False
        new_node.selected = True
        self.current_node = new_node

    def _select_node_at_index(self, index: int) -> None:
        """选择指定索引的节点"""
        visible_nodes = self._get_visible_nodes()
        if 0 <= index < len(visible_nodes):
            self._select_node(visible_nodes[index])