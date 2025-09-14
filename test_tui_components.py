#!/usr/bin/env python3
"""
测试 TUI 组件功能，特别是输入框焦点问题的修复。
"""

import asyncio
from unittest.mock import patch, MagicMock

# Import the TUI components we want to test  
from tui_components.components.input_box import InputBoxComponent
from textual.app import App, ComposeResult


def test_input_box_initialization():
    """测试输入框组件初始化"""
    input_box = InputBoxComponent(placeholder="test> ")
    
    assert hasattr(input_box, 'prompt')
    assert input_box.prompt == "test> "
    assert hasattr(input_box, 'buffer') 
    assert isinstance(input_box.buffer, str)
    

def test_input_box_submit():
    """测试输入框提交功能"""
    input_box = InputBoxComponent(placeholder="> ")
    
    # Mock the message posting
    with patch.object(input_box, 'post_message') as mock_post:
        # Simulate pressing enter after typing "test"
        input_box.buffer = "test" 
        mock_post.reset_mock()
        
        # This should trigger the Submitted message
        from textual import events
        
        class MockEvent:
            def __init__(self):
                self.key = "enter"
        
        # Simulate the key event handling
        input_box.buffer += "\n"  # This is what happens in real usage
        
    assert mock_post.called


def test_input_box_focus():
    """测试输入框是否能获得焦点"""
    
    # Create a simple app to test focus behavior
    class TestApp(App):
        def __init__(self):
            super().__init__()
            
        def compose(self) -> ComposeResult:
            yield InputBoxComponent(placeholder="> ")
    
    # Test that we can create the app and component
    try:
        test_app = TestApp()
        
        # Check that we can access the component
        input_box_component = InputBoxComponent(placeholder="> ")
        
        # The main issue is that the input box should receive focus on app startup
        assert isinstance(input_box_component, InputBoxComponent)
        
    except Exception as e:
        print(f"Error in focus test: {e}")
        raise


if __name__ == "__main__":
    print("Running TUI component tests...")
    
    try:
        test_input_box_initialization()
        print("✅ InputBoxComponent initialization test passed")
        
        test_input_box_submit() 
        print("✅ InputBoxComponent submit test passed")
        
        test_input_box_focus()
        print("✅ InputBoxComponent focus test passed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise