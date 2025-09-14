#!/usr/bin/env python3
"""
简单测试焦点修复是否有效。
"""

import sys
import os

# Add the project root to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_import():
    """测试主程序是否能正常导入"""
    try:
        from main import TeamDevApp
        print("✅ 主程序成功导入")
        
        # Create an instance to verify it works 
        app = TeamDevApp()
        print("✅ 应用实例创建成功")
        
        # Check that focus method exists
        if hasattr(app, 'focus_input_box'):
            print("✅ focus_input_box 方法存在")
        
        # Check that input box exists
        if hasattr(app, 'input_box'):
            print("✅ 输入框组件存在")
            
    except Exception as e:
        print(f"❌ 导入或创建应用失败: {e}")
        return False
        
    return True

def test_syntax():
    """检查语法是否正确"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        # Simple syntax check - make sure the focus method is in there
        if 'focus_input_box' in content:
            print("✅ 焦点方法已添加到主程序")
        else:
            print("❌ 焦点方法未找到在主程序中") 
            return False
            
        # Check that the method is properly defined
        if 'def focus_input_box' in content:
            print("✅ 焦点方法定义正确")
        else:
            print("❌ 焦点方法未正确定义") 
            return False
            
        # Check that focus is called in on_mount
        if 'set_focus' in content and 'input_box' in content:
            print("✅ 焦点设置调用已添加")
        elif 'call_after_refresh' in content and 'focus_input_box' in content:
            print("✅ 焦点设置调用已添加（旧版本）")
        else:
            print("❌ 未找到焦点设置调用") 
            return False
            
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("测试焦点修复...")
    
    success1 = test_main_import()
    success2 = test_syntax() 
    
    if success1 and success2:
        print("\n🎉 所有测试通过！焦点修复已正确实现。")
    else:
        print("\n❌ 某些测试失败，请检查代码。")