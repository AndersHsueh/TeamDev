"""
布局管理器
负责组件的布局和排列
"""

from typing import List, Optional, Tuple
from enum import Enum
from .base_component import BaseComponent, Rect, Position, Size


class LayoutType(Enum):
    """布局类型"""
    HORIZONTAL = "horizontal"  # 水平布局
    VERTICAL = "vertical"      # 垂直布局
    GRID = "grid"             # 网格布局
    ABSOLUTE = "absolute"     # 绝对定位


class Alignment(Enum):
    """对齐方式"""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class LayoutManager:
    """布局管理器"""
    
    def __init__(self):
        self.layout_type = LayoutType.VERTICAL
        self.alignment = Alignment.START
        self.spacing = 1
        self.padding = 0
        self.grid_columns = 1
    
    def set_layout_type(self, layout_type: LayoutType) -> None:
        """设置布局类型"""
        self.layout_type = layout_type
    
    def set_alignment(self, alignment: Alignment) -> None:
        """设置对齐方式"""
        self.alignment = alignment
    
    def set_spacing(self, spacing: int) -> None:
        """设置间距"""
        self.spacing = spacing
    
    def set_padding(self, padding: int) -> None:
        """设置内边距"""
        self.padding = padding
    
    def set_grid_columns(self, columns: int) -> None:
        """设置网格列数"""
        self.grid_columns = columns
    
    def layout_components(self, container: BaseComponent, available_rect: Rect) -> None:
        """
        布局组件
        container: 容器组件
        available_rect: 可用区域
        """
        if not container.children:
            return
        
        # 计算可用空间（减去内边距）
        content_rect = Rect(
            available_rect.x + self.padding,
            available_rect.y + self.padding,
            available_rect.width - 2 * self.padding,
            available_rect.height - 2 * self.padding
        )
        
        if self.layout_type == LayoutType.HORIZONTAL:
            self._layout_horizontal(container.children, content_rect)
        elif self.layout_type == LayoutType.VERTICAL:
            self._layout_vertical(container.children, content_rect)
        elif self.layout_type == LayoutType.GRID:
            self._layout_grid(container.children, content_rect)
        elif self.layout_type == LayoutType.ABSOLUTE:
            # 绝对定位不进行自动布局
            pass
    
    def _layout_horizontal(self, children: List[BaseComponent], rect: Rect) -> None:
        """水平布局"""
        if not children:
            return
        
        # 计算每个组件的宽度
        total_spacing = (len(children) - 1) * self.spacing
        available_width = rect.width - total_spacing
        
        if self.alignment == Alignment.STRETCH:
            # 拉伸模式：平均分配宽度
            child_width = available_width // len(children)
            for i, child in enumerate(children):
                child.set_position(rect.x + i * (child_width + self.spacing), rect.y)
                child.set_size(child_width, rect.height)
        else:
            # 其他模式：使用组件自身宽度
            current_x = rect.x
            for child in children:
                child.set_position(current_x, rect.y)
                # 保持组件原有高度，或使用容器高度
                child_height = min(child.size.height, rect.height) if child.size.height > 0 else rect.height
                child.set_size(child.size.width, child_height)
                current_x += child.size.width + self.spacing
    
    def _layout_vertical(self, children: List[BaseComponent], rect: Rect) -> None:
        """垂直布局"""
        if not children:
            return
        
        # 计算每个组件的高度
        total_spacing = (len(children) - 1) * self.spacing
        available_height = rect.height - total_spacing
        
        if self.alignment == Alignment.STRETCH:
            # 拉伸模式：平均分配高度
            child_height = available_height // len(children)
            for i, child in enumerate(children):
                child.set_position(rect.x, rect.y + i * (child_height + self.spacing))
                child.set_size(rect.width, child_height)
        else:
            # 其他模式：使用组件自身高度
            current_y = rect.y
            for child in children:
                child.set_position(rect.x, current_y)
                # 保持组件原有宽度，或使用容器宽度
                child_width = min(child.size.width, rect.width) if child.size.width > 0 else rect.width
                child.set_size(child_width, child.size.height)
                current_y += child.size.height + self.spacing
    
    def _layout_grid(self, children: List[BaseComponent], rect: Rect) -> None:
        """网格布局"""
        if not children:
            return
        
        rows = (len(children) + self.grid_columns - 1) // self.grid_columns
        cell_width = (rect.width - (self.grid_columns - 1) * self.spacing) // self.grid_columns
        cell_height = (rect.height - (rows - 1) * self.spacing) // rows
        
        for i, child in enumerate(children):
            row = i // self.grid_columns
            col = i % self.grid_columns
            
            x = rect.x + col * (cell_width + self.spacing)
            y = rect.y + row * (cell_height + self.spacing)
            
            child.set_position(x, y)
            child.set_size(cell_width, cell_height)
    
    def calculate_size(self, children: List[BaseComponent]) -> Size:
        """计算布局所需的总尺寸"""
        if not children:
            return Size(0, 0)
        
        if self.layout_type == LayoutType.HORIZONTAL:
            total_width = sum(child.size.width for child in children)
            total_width += (len(children) - 1) * self.spacing
            max_height = max(child.size.height for child in children) if children else 0
            return Size(total_width + 2 * self.padding, max_height + 2 * self.padding)
        
        elif self.layout_type == LayoutType.VERTICAL:
            max_width = max(child.size.width for child in children) if children else 0
            total_height = sum(child.size.height for child in children)
            total_height += (len(children) - 1) * self.spacing
            return Size(max_width + 2 * self.padding, total_height + 2 * self.padding)
        
        elif self.layout_type == LayoutType.GRID:
            rows = (len(children) + self.grid_columns - 1) // self.grid_columns
            max_cell_width = max(child.size.width for child in children) if children else 0
            max_cell_height = max(child.size.height for child in children) if children else 0
            
            total_width = self.grid_columns * max_cell_width + (self.grid_columns - 1) * self.spacing
            total_height = rows * max_cell_height + (rows - 1) * self.spacing
            return Size(total_width + 2 * self.padding, total_height + 2 * self.padding)
        
        return Size(0, 0)
