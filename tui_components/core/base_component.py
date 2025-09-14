"""
TUI 组件基类
定义所有组件的通用接口和基础功能
"""
from textual.widget import Widget
from abc import abstractmethod
from typing import Any, Optional

class BaseComponent(Widget):
    """所有 TUI 组件的基类, 继承自 Textual Widget"""

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    @abstractmethod
    def update(self, data: Any = None) -> None:
        """
        更新组件状态
        data: 更新数据
        """
        pass

