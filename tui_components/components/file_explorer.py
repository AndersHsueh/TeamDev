"""
文件浏览树组件
显示文件系统目录结构
"""

import os
from typing import List, Dict, Any, Optional, Callable
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style


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
            # 根据文件扩展名返回不同图标
            ext = os.path.splitext(self.name)[1].lower()
            icon_map = {
                '.py': '🐍',
                '.js': '📜',
                '.html': '🌐',
                '.css': '🎨',
                '.json': '📋',
                '.md': '📝',
                '.txt': '📄',
                '.png': '🖼️',
                '.jpg': '🖼️',
                '.gif': '🖼️',
                '.zip': '📦',
                '.pdf': '📕',
            }
            return icon_map.get(ext, '📄')
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return f"{self.get_icon()} {self.name}"


class FileExplorerComponent(BaseComponent):
    """文件浏览树组件"""
    
    def __init__(self, name: str = "file_explorer"):
        super().__init__(name)
        self.root_path = "."
        self.root_node: Optional[FileNode] = None
        self.current_node: Optional[FileNode] = None
        self.scroll_offset = 0
        self.max_visible_items = 0
        self.on_file_select: Optional[Callable[[str], None]] = None
        self.on_dir_expand: Optional[Callable[[str], None]] = None
        self.hidden_files = True  # 是否显示隐藏文件
        self.file_filter: Optional[Callable[[str], bool]] = None
        
        # 样式配置
        self.indent_size = 2
        self.selected_color = get_color("selection")
        self.directory_color = get_color("primary")
        self.file_color = get_color("text")
        self.hidden_color = get_color("text_muted")
    
    def set_root_path(self, path: str) -> None:
        """设置根路径"""
        self.root_path = path
        self._build_tree()
    
    def set_file_select_callback(self, callback: Callable[[str], None]) -> None:
        """设置文件选择回调"""
        self.on_file_select = callback
    
    def set_dir_expand_callback(self, callback: Callable[[str], None]) -> None:
        """设置目录展开回调"""
        self.on_dir_expand = callback
    
    def set_hidden_files(self, show: bool) -> None:
        """设置是否显示隐藏文件"""
        self.hidden_files = show
        self._build_tree()
    
    def set_file_filter(self, filter_func: Callable[[str], bool]) -> None:
        """设置文件过滤器"""
        self.file_filter = filter_func
        self._build_tree()
    
    def _build_tree(self) -> None:
        """构建文件树"""
        if not os.path.exists(self.root_path):
            self.root_node = None
            return
        
        self.root_node = FileNode(self.root_path, os.path.basename(self.root_path), True)
        self._build_node_children(self.root_node)
        self.current_node = self.root_node
    
    def _build_node_children(self, node: FileNode) -> None:
        """构建节点的子节点"""
        if not node.is_dir:
            return
        
        try:
            items = os.listdir(node.path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(node.path, x)), x.lower()))
            
            for item in items:
                item_path = os.path.join(node.path, item)
                
                # 检查是否显示隐藏文件
                if not self.hidden_files and item.startswith('.'):
                    continue
                
                # 检查文件过滤器
                if self.file_filter and not self.file_filter(item_path):
                    continue
                
                is_dir = os.path.isdir(item_path)
                child_node = FileNode(item_path, item, is_dir)
                node.add_child(child_node)
                
                # 如果是目录，递归构建子节点（但默认不展开）
                if is_dir:
                    self._build_node_children(child_node)
        
        except PermissionError:
            # 没有权限访问目录
            pass
    
    def _get_visible_nodes(self) -> List[FileNode]:
        """获取可见的节点列表（扁平化）"""
        if not self.root_node:
            return []
        
        visible_nodes = []
        self._flatten_nodes(self.root_node, visible_nodes, 0)
        return visible_nodes
    
    def _flatten_nodes(self, node: FileNode, result: List[FileNode], level: int) -> None:
        """扁平化节点树"""
        result.append(node)
        
        if node.is_dir and node.expanded:
            for child in node.children:
                self._flatten_nodes(child, result, level + 1)
    
    def _get_node_at_index(self, index: int) -> Optional[FileNode]:
        """获取指定索引的节点"""
        visible_nodes = self._get_visible_nodes()
        if 0 <= index < len(visible_nodes):
            return visible_nodes[index]
        return None
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        lines = []
        visible_nodes = self._get_visible_nodes()
        self.max_visible_items = self.size.height
        
        # 计算显示范围
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_items, len(visible_nodes))
        
        for i in range(start_idx, end_idx):
            if i >= len(visible_nodes):
                break
            
            node = visible_nodes[i]
            line = self._render_node(node, i)
            lines.append(line)
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_node(self, node: FileNode, index: int) -> str:
        """渲染单个节点"""
        # 计算缩进
        level = self._get_node_level(node)
        indent = " " * (level * self.indent_size)
        
        # 获取显示名称
        display_name = node.get_display_name()
        
        # 应用颜色
        if node.selected:
            color = self.selected_color
        elif node.is_dir:
            color = self.directory_color
        elif node.name.startswith('.'):
            color = self.hidden_color
        else:
            color = self.file_color
        
        # 构建行内容
        line = f"{indent}{display_name}"
        
        # 截断过长的行
        max_width = self.size.width
        if len(line) > max_width:
            line = line[:max_width-3] + "..."
        
        # 应用颜色（如果支持）
        if color:
            line = f"[{color}]{line}[/{color}]"
        
        return line
    
    def _get_node_level(self, node: FileNode) -> int:
        """获取节点层级"""
        level = 0
        current = node.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "root_path" in data:
                self.set_root_path(data["root_path"])
            if "hidden_files" in data:
                self.set_hidden_files(data["hidden_files"])
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        if not self.visible:
            return False
        
        visible_nodes = self._get_visible_nodes()
        if not visible_nodes:
            return False
        
        current_index = self._get_current_node_index()
        
        if key == "up" or key == "k":
            # 向上移动
            if current_index > 0:
                self._select_node_at_index(current_index - 1)
                self._ensure_visible(current_index - 1)
            return True
        
        elif key == "down" or key == "j":
            # 向下移动
            if current_index < len(visible_nodes) - 1:
                self._select_node_at_index(current_index + 1)
                self._ensure_visible(current_index + 1)
            return True
        
        elif key == "enter" or key == " ":
            # 选择节点
            if current_index >= 0:
                node = visible_nodes[current_index]
                if node.is_dir:
                    self._toggle_expand(node)
                    if self.on_dir_expand:
                        self.on_dir_expand(node.path)
                else:
                    if self.on_file_select:
                        self.on_file_select(node.path)
            return True
        
        elif key == "left" or key == "h":
            # 折叠当前目录
            if current_index >= 0:
                node = visible_nodes[current_index]
                if node.is_dir and node.expanded:
                    node.expanded = False
            return True
        
        elif key == "right" or key == "l":
            # 展开当前目录
            if current_index >= 0:
                node = visible_nodes[current_index]
                if node.is_dir and not node.expanded:
                    node.expanded = True
            return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        if not self.visible:
            return False
        
        # 计算点击的节点索引
        clicked_index = self.scroll_offset + y
        visible_nodes = self._get_visible_nodes()
        
        if 0 <= clicked_index < len(visible_nodes):
            node = visible_nodes[clicked_index]
            self._select_node_at_index(clicked_index)
            
            if button == 1:  # 左键
                if node.is_dir:
                    self._toggle_expand(node)
                    if self.on_dir_expand:
                        self.on_dir_expand(node.path)
                else:
                    if self.on_file_select:
                        self.on_file_select(node.path)
            return True
        
        return False
    
    def _get_current_node_index(self) -> int:
        """获取当前选中节点的索引"""
        visible_nodes = self._get_visible_nodes()
        for i, node in enumerate(visible_nodes):
            if node.selected:
                return i
        return 0
    
    def _select_node_at_index(self, index: int) -> None:
        """选择指定索引的节点"""
        visible_nodes = self._get_visible_nodes()
        
        # 清除所有选择
        for node in visible_nodes:
            node.selected = False
        
        # 选择新节点
        if 0 <= index < len(visible_nodes):
            visible_nodes[index].selected = True
            self.current_node = visible_nodes[index]
    
    def _toggle_expand(self, node: FileNode) -> None:
        """切换节点展开状态"""
        if node.is_dir:
            node.expanded = not node.expanded
    
    def _ensure_visible(self, index: int) -> None:
        """确保指定索引的节点可见"""
        if index < self.scroll_offset:
            self.scroll_offset = index
        elif index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = index - self.max_visible_items + 1
    
    def get_selected_path(self) -> Optional[str]:
        """获取当前选中的路径"""
        if self.current_node:
            return self.current_node.path
        return None
    
    def expand_path(self, path: str) -> bool:
        """展开到指定路径"""
        if not self.root_node:
            return False
        
        # 查找并展开路径上的所有目录
        relative_path = os.path.relpath(path, self.root_path)
        path_parts = relative_path.split(os.sep)
        
        current_node = self.root_node
        for part in path_parts:
            if part == "." or part == "":
                continue
            
            found = False
            for child in current_node.children:
                if child.name == part:
                    if child.is_dir:
                        child.expanded = True
                        current_node = child
                        found = True
                        break
            
            if not found:
                return False
        
        return True
