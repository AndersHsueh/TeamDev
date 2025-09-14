"""
弹出窗口组件
可以在屏幕中间弹出，显示重要信息或选择项，具有模态对话框功能
用户必须选择 Ok/Cancel 才能继续操作其他界面
"""

from typing import Optional, Callable, List, Any
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Button
from textual.screen import ModalScreen
from textual.events import Key
from ..core.base_component import BaseComponent


class PopupChoice:
    """弹出窗口的选择项"""
    
    def __init__(self, label: str, value: Any = None, callback: Optional[Callable] = None):
        self.label = label
        self.value = value if value is not None else label
        self.callback = callback


class PopupWinComponent(ModalScreen[Any]):
    """
    弹出窗口组件 - 模态对话框
    
    功能：
    - 在屏幕中间显示弹出窗口
    - 显示标题、消息内容
    - 提供 Ok/Cancel 按钮或自定义选择项
    - 模态显示，阻止用户操作其他界面
    - 支持键盘快捷键（Enter=Ok, Escape=Cancel）
    """
    
    DEFAULT_CSS = """
    PopupWinComponent {
        align: center middle;
    }
    
    #popup_container {
        width: 60%;
        height: auto;
        max-width: 80;
        max-height: 20;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #popup_title {
        height: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #popup_message {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        text-align: center;
    }
    
    #popup_buttons {
        height: 3;
        align: center middle;
    }
    
    .popup_button {
        width: 12;
        margin: 0 1;
    }
    
    .popup_button_ok {
        background: $success;
        color: $text;
    }
    
    .popup_button_cancel {
        background: $error;
        color: $text;
    }
    
    .popup_button_choice {
        background: $accent;
        color: $text;
    }
    """
    
    def __init__(
        self,
        title: str = "提示",
        message: str = "",
        choices: Optional[List[PopupChoice]] = None,
        ok_callback: Optional[Callable] = None,
        cancel_callback: Optional[Callable] = None,
        show_cancel: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.popup_title = title
        self.popup_message = message
        self.choices = choices or []
        self.ok_callback = ok_callback
        self.cancel_callback = cancel_callback
        self.show_cancel = show_cancel
        self.result_value: Any = None
    
    def compose(self) -> ComposeResult:
        """构建弹出窗口布局"""
        with Container(id="popup_container"):
            # 标题栏
            yield Static(self.popup_title, id="popup_title")
            
            # 消息内容
            if self.popup_message:
                yield Static(self.popup_message, id="popup_message")
            
            # 按钮区域
            with Horizontal(id="popup_buttons"):
                # 如果有自定义选择项
                if self.choices:
                    for choice in self.choices:
                        yield Button(
                            choice.label,
                            id=f"choice_{hash(choice.label)}",
                            classes="popup_button popup_button_choice"
                        )
                else:
                    # 默认 Ok 按钮
                    yield Button(
                        "确定",
                        id="popup_ok",
                        classes="popup_button popup_button_ok"
                    )
                
                # Cancel 按钮
                if self.show_cancel:
                    yield Button(
                        "取消",
                        id="popup_cancel",
                        classes="popup_button popup_button_cancel"
                    )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        
        if button_id == "popup_ok":
            self.result_value = True
            if self.ok_callback:
                self.ok_callback(True)
            self.dismiss(True)
        
        elif button_id == "popup_cancel":
            self.result_value = False
            if self.cancel_callback:
                self.cancel_callback(False)
            self.dismiss(False)
        
        elif button_id and button_id.startswith("choice_"):
            # 处理自定义选择项
            button_text = event.button.label
            for choice in self.choices:
                if choice.label == button_text:
                    self.result_value = choice.value
                    if choice.callback:
                        choice.callback(choice.value)
                    self.dismiss(choice.value)
                    break
    
    def on_key(self, event: Key) -> None:
        """处理键盘事件"""
        if event.key == "enter":
            # Enter 键相当于点击 Ok 按钮
            if not self.choices:  # 只有在没有自定义选择项时才响应
                self.result_value = True
                if self.ok_callback:
                    self.ok_callback(True)
                self.dismiss(True)
        
        elif event.key == "escape":
            # Escape 键相当于点击 Cancel 按钮
            if self.show_cancel:
                self.result_value = False
                if self.cancel_callback:
                    self.cancel_callback(False)
                self.dismiss(False)


class PopupWinHelper:
    """弹出窗口辅助类，提供快捷方法"""
    
    @staticmethod
    def show_info(
        app,
        title: str = "信息",
        message: str = "",
        ok_callback: Optional[Callable] = None
    ) -> PopupWinComponent:
        """显示信息弹出窗口（只有 Ok 按钮）"""
        popup = PopupWinComponent(
            title=title,
            message=message,
            ok_callback=ok_callback,
            show_cancel=False
        )
        app.push_screen(popup)
        return popup
    
    @staticmethod
    def show_confirm(
        app,
        title: str = "确认",
        message: str = "",
        ok_callback: Optional[Callable] = None,
        cancel_callback: Optional[Callable] = None
    ) -> PopupWinComponent:
        """显示确认弹出窗口（Ok 和 Cancel 按钮）"""
        popup = PopupWinComponent(
            title=title,
            message=message,
            ok_callback=ok_callback,
            cancel_callback=cancel_callback,
            show_cancel=True
        )
        app.push_screen(popup)
        return popup
    
    @staticmethod
    def show_choices(
        app,
        choices: List[PopupChoice],
        title: str = "选择",
        message: str = "",
        show_cancel: bool = True,
        cancel_callback: Optional[Callable] = None
    ) -> PopupWinComponent:
        """显示多选项弹出窗口"""
        popup = PopupWinComponent(
            title=title,
            message=message,
            choices=choices,
            cancel_callback=cancel_callback,
            show_cancel=show_cancel
        )
        app.push_screen(popup)
        return popup


# 使用示例和测试代码
if __name__ == "__main__":
    from textual.app import App
    
    class PopupTestApp(App):
        """测试弹出窗口组件的应用"""
        
        CSS = """
        Screen {
            background: $surface;
            align: center middle;
        }
        
        #test_buttons {
            height: auto;
            width: auto;
            background: $panel;
            padding: 2;
        }
        
        .test_button {
            width: 20;
            margin: 1;
        }
        """
        
        def compose(self) -> ComposeResult:
            with Vertical(id="test_buttons"):
                yield Static("弹出窗口组件测试", classes="test_title")
                yield Button("信息弹窗", id="test_info", classes="test_button")
                yield Button("确认弹窗", id="test_confirm", classes="test_button")
                yield Button("选择弹窗", id="test_choices", classes="test_button")
        
        def on_button_pressed(self, event: Button.Pressed) -> None:
            button_id = event.button.id
            
            if button_id == "test_info":
                PopupWinHelper.show_info(
                    self,
                    title="系统信息",
                    message="这是一个信息提示弹窗\n只有确定按钮",
                    ok_callback=lambda x: self.bell()
                )
            
            elif button_id == "test_confirm":
                PopupWinHelper.show_confirm(
                    self,
                    title="确认操作",
                    message="您确定要执行此操作吗？\n此操作不可撤销",
                    ok_callback=lambda x: self.bell(),
                    cancel_callback=lambda x: None
                )
            
            elif button_id == "test_choices":
                choices = [
                    PopupChoice("选项 A", "option_a", lambda x: self.bell()),
                    PopupChoice("选项 B", "option_b", lambda x: self.bell()),
                    PopupChoice("选项 C", "option_c", lambda x: self.bell()),
                ]
                PopupWinHelper.show_choices(
                    self,
                    choices,
                    title="选择操作",
                    message="请选择一个操作：",
                    cancel_callback=lambda x: None
                )
    
    # 运行测试应用
    PopupTestApp().run()