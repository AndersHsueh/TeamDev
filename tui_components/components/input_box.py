import textwrap
from core.base_component import BaseComponent
from wcwidth import wcswidth


class InputBox(BaseComponent):
    def __init__(self, prompt: str = "> ", width: int = 80):
        super().__init__(name="InputBox")
        self.prompt = prompt
        self.width = width
        self.buffer = ""          # 当前输入缓冲
        self.history = []         # 历史输入
        self.history_index = -1   # 当前历史索引

    def render(self) -> str:
        """
        渲染输入框，带 prompt，支持自动换行。
        """
        full_text = self.prompt + self.buffer
        wrapped_lines = textwrap.wrap(full_text, self.width,
                                      replace_whitespace=False,
                                      drop_whitespace=False)
        return "\n".join(wrapped_lines)

    def update(self, data=None) -> None:
        """这里不需要定时更新，由 handle_key 驱动。"""
        pass

    def handle_key(self, key: str) -> str | None:
        """
        处理键盘输入：
        - 普通字符：加入 buffer
        - Backspace：删除一个完整字符
        - Enter：提交输入，存入历史，并清空 buffer
        - 上/下键：浏览历史
        返回值：如果按下 Enter，返回提交的字符串，否则 None
        """
        if key == "Backspace":
            if self.buffer:
                self.buffer = self.buffer[:-1]
        elif key == "Enter":
            if self.buffer.strip():
                self.history.append(self.buffer)
                self.history_index = len(self.history)
                submitted = self.buffer
                self.buffer = ""
                return submitted
        elif key == "Up":
            if self.history:
                self.history_index = max(0, self.history_index - 1)
                self.buffer = self.history[self.history_index]
        elif key == "Down":
            if self.history:
                self.history_index = min(len(self.history), self.history_index + 1)
                if self.history_index == len(self.history):
                    self.buffer = ""
                else:
                    self.buffer = self.history[self.history_index]
        else:
            # 普通字符输入，包含中文
            self.buffer += key
        return None