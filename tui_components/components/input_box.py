from typing import Optional
import textwrap
from ..core.base_component import BaseComponent
from textual.message import Message
from textual import events

class InputBoxComponent(BaseComponent):
    """A simple input box component for Textual."""

    # Enable this component to receive focus
    can_focus = True

    class Submitted(Message):
        """Posted when the user presses Enter."""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(
        self,
        *, 
        id: Optional[str] = None,
        classes: Optional[str] = None,
        name: Optional[str] = None,
        placeholder: str = "> ",
    ):
        super().__init__(id=id, classes=classes, name=name)
        self.prompt = placeholder
        self.buffer = ""
        self.history = []
        self.history_index = -1

    def render(self) -> str:
        """Render the input box with cursor."""
        # Add cursor at the end of buffer when component has focus
        cursor = "█" if self.has_focus else ""
        full_text = self.prompt + self.buffer + cursor
        
        # Use self.size.width which is provided by Textual's Widget
        try:
            width = self.size.width if hasattr(self, 'size') and self.size.width > 0 else 80
        except:
            width = 80
            
        wrapped_lines = textwrap.wrap(full_text, width,
                                      replace_whitespace=False,
                                      drop_whitespace=False)
        
        # If no content, ensure at least one line is shown
        if not wrapped_lines:
            wrapped_lines = [self.prompt + cursor]
            
        return "\n".join(wrapped_lines)

    def update(self, data=None) -> None:
        """No periodic updates needed for this component."""
        pass

    async def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        key = event.key
        
        if key == "backspace":
            if self.buffer:
                self.buffer = self.buffer[:-1]
                self.refresh()
        elif key == "enter":
            if self.buffer.strip():
                self.history.append(self.buffer)
                self.history_index = len(self.history)
                self.post_message(self.Submitted(self.buffer))
                self.buffer = ""
                self.refresh()
        elif key == "up":
            if self.history:
                self.history_index = max(0, self.history_index - 1)
                self.buffer = self.history[self.history_index]
                self.refresh()
        elif key == "down":
            if self.history:
                self.history_index = min(len(self.history), self.history_index + 1)
                if self.history_index == len(self.history):
                    self.buffer = ""
                else:
                    self.buffer = self.history[self.history_index]
                self.refresh()
        elif event.is_printable and key != "ctrl+q":
            # Handle printable characters but exclude Ctrl+Q to allow proper exit
            self.buffer += event.character
            self.refresh()

        # Mark the event as handled so it doesn't propagate
        event.stop()

    def clear(self) -> None:
        """Clear the input buffer."""
        self.buffer = ""
        self.refresh()

    def set_value(self, value: str) -> None:
        """Set the input buffer value."""
        self.buffer = value
        self.refresh()

    def on_focus(self) -> None:
        """Called when the widget gains focus."""
        self.refresh()  # Refresh to show cursor

    def on_blur(self) -> None:
        """Called when the widget loses focus."""
        self.refresh()  # Refresh to hide cursor
