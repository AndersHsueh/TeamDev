"""
TUI 组件基类
定义所有组件的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Position:
    """位置信息"""
    x: int
    y: int


@dataclass
class Size:
    """尺寸信息"""
    width: int
    height: int


@dataclass
class Rect:
    """矩形区域"""
    x: int
    y: int
    width: int
    height: int


class BaseComponent(ABC):
    """所有 TUI 组件的基类"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.position = Position(0, 0)
        self.size = Size(0, 0)
        self.visible = True
        self.focused = False
        self.parent: Optional['BaseComponent'] = None
        self.children: list['BaseComponent'] = []
        self.attributes: Dict[str, Any] = {}
    
    @abstractmethod
    def render(self) -> str:
        """
        渲染组件内容
        返回要显示的字符串
        """
        pass
    
    @abstractmethod
    def update(self, data: Any = None) -> None:
        """
        更新组件状态
        data: 更新数据
        """
        pass
    
    def set_position(self, x: int, y: int) -> None:
        """设置组件位置"""
        self.position = Position(x, y)
    
    def set_size(self, width: int, height: int) -> None:
        """设置组件尺寸"""
        self.size = Size(width, height)
    
    def get_rect(self) -> Rect:
        """获取组件矩形区域"""
        return Rect(
            self.position.x,
            self.position.y,
            self.size.width,
            self.size.height
        )
    
    def add_child(self, child: 'BaseComponent') -> None:
        """添加子组件"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'BaseComponent') -> None:
        """移除子组件"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def set_visible(self, visible: bool) -> None:
        """设置可见性"""
        self.visible = visible
    
    def set_focused(self, focused: bool) -> None:
        """设置焦点状态"""
        self.focused = focused
    
    def handle_key(self, key: str) -> bool:
        """
        处理键盘输入
        返回 True 表示已处理，False 表示未处理
        """
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """
        处理鼠标事件
        返回 True 表示已处理，False 表示未处理
        """
        return False
    
    def is_point_inside(self, x: int, y: int) -> bool:
        """检查点是否在组件内"""
        rect = self.get_rect()
        return (rect.x <= x < rect.x + rect.width and
                rect.y <= y < rect.y + rect.height)
    
    def get_absolute_position(self) -> Position:
        """获取绝对位置（考虑父组件位置）"""
        if self.parent:
            parent_pos = self.parent.get_absolute_position()
            return Position(
                parent_pos.x + self.position.x,
                parent_pos.y + self.position.y
            )
        return self.position
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', pos=({self.position.x}, {self.position.y}), size=({self.size.width}, {self.size.height}))"
