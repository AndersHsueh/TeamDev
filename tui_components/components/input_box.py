import textwrap
from ..core.base_component import BaseComponent
from textual.message import Message
from textual import events

class InputBoxComponent(BaseComponent):
    """A simple input box component for Textual."""

    class Submitted(Message):
        """Posted when the user presses Enter."""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(
        self,
        *, 
        id: str | None = None,
        classes: str | None = None,
        name: str | None = None,
        placeholder: str = "> ",
    ):
        super().__init__(id=id, classes=classes, name=name)
        self.prompt = placeholder
        self.buffer = ""
        self.history = []
        self.history_index = -1

    def render(self) -> str:
        """Render the input box."""
        full_text = self.prompt + self.buffer
        # Use self.size.width which is provided by Textual's Widget
        wrapped_lines = textwrap.wrap(full_text, self.size.width or 80,
                                      replace_whitespace=False,
                                      drop_whitespace=False)
        return "\n".join(wrapped_lines)

    def update(self, data=None) -> None:
        """No periodic updates needed for this component."""
        pass

    async def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        event.stop()
        key = event.key
        
        if key == "backspace":
            if self.buffer:
                self.buffer = self.buffer[:-1]
        elif key == "enter":
            if self.buffer.strip():
                self.history.append(self.buffer)
                self.history_index = len(self.history)
                self.post_message(self.Submitted(self.buffer))
                self.buffer = ""
        elif key == "up":
            if self.history:
                self.history_index = max(0, self.history_index - 1)
                self.buffer = self.history[self.history_index]
        elif key == "down":
            if self.history:
                self.history_index = min(len(self.history), self.history_index + 1)
                if self.history_index == len(self.history):
                    self.buffer = ""
                else:
                    self.buffer = self.history[self.history_index]
        elif event.is_printable:
            self.buffer += event.character

        self.refresh()
