"""
TUI 组件基类
定义所有组件的通用接口和基础功能
"""
from textual.widget import Widget
from abc import abstractmethod
from typing import Any

class BaseComponent(Widget):
    """所有 TUI 组件的基类, 继承自 Textual Widget"""

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
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

