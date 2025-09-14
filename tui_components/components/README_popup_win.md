# PopupWin 弹出窗口组件使用指南

## 📋 功能概述

`popup_win.py` 是一个功能完整的模态弹出窗口组件，专为 TeamDev TUI 界面设计。

### ✨ 主要特性

- 🎯 **模态显示** - 阻止用户操作其他界面元素
- 📍 **居中显示** - 自动在屏幕中心显示
- ⌨️ **键盘支持** - Enter确定, Escape取消
- 🎨 **主题一致** - 与项目整体样式保持一致
- 🔧 **高度可定制** - 支持多种显示模式

## 📦 组件结构

### PopupChoice 类
```python
class PopupChoice:
    def __init__(self, label: str, value: Any = None, callback: Optional[Callable] = None)
```
- `label`: 选择项显示文本
- `value`: 选择项返回值（默认为label）
- `callback`: 选择后的回调函数

### PopupWinComponent 类
主弹出窗口组件，继承自 `ModalScreen`。

### PopupWinHelper 辅助类
提供快捷方法创建常用弹出窗口。

## 🚀 使用方法

### 1. 信息弹窗（只有确定按钮）

```python
from tui_components.components.popup_win import PopupWinHelper

# 显示信息提示
PopupWinHelper.show_info(
    app,                           # 应用实例
    title="系统信息",              # 标题
    message="操作已完成！",        # 消息内容
    ok_callback=lambda x: print("用户确认")  # 确定回调
)
```

### 2. 确认弹窗（确定和取消按钮）

```python
def on_confirm(result):
    if result:
        print("用户确认操作")
    else:
        print("用户取消操作")

PopupWinHelper.show_confirm(
    app,
    title="确认删除",
    message="您确定要删除此文件吗？\n此操作不可撤销",
    ok_callback=lambda x: on_confirm(True),
    cancel_callback=lambda x: on_confirm(False)
)
```

### 3. 选择弹窗（多个选择项）

```python
# 定义选择项
choices = [
    PopupChoice("新建项目", "new", lambda x: create_project()),
    PopupChoice("打开项目", "open", lambda x: open_project()),
    PopupChoice("导入项目", "import", lambda x: import_project()),
]

PopupWinHelper.show_choices(
    app,
    choices,                       # 选择项列表
    title="项目操作",              # 标题
    message="请选择要执行的操作：", # 消息
    show_cancel=True,              # 显示取消按钮
    cancel_callback=lambda x: print("用户取消")
)
```

### 4. 直接使用 PopupWinComponent

```python
# 创建自定义弹出窗口
popup = PopupWinComponent(
    title="自定义弹窗",
    message="这是自定义内容",
    choices=[
        PopupChoice("选项1", 1),
        PopupChoice("选项2", 2),
    ],
    show_cancel=False
)

# 显示弹出窗口
app.push_screen(popup)

# 获取结果（异步）
result = await popup.wait_for_dismiss()
print(f"用户选择: {result}")
```

## ⌨️ 键盘快捷键

| 按键 | 功能 |
|------|------|
| `Enter` | 确定（仅在无自定义选择项时） |
| `Escape` | 取消（如果显示取消按钮） |
| `Tab` | 在按钮间切换焦点 |
| `Space` | 激活当前焦点按钮 |

## 🎨 样式定制

组件使用项目统一的 CSS 变量：

- `$surface` - 弹窗背景
- `$primary` - 边框和标题背景
- `$success` - 确定按钮背景
- `$error` - 取消按钮背景
- `$accent` - 选择按钮背景

## 📝 使用示例

查看 `test_popup_win.py` 文件了解完整的使用示例，包括：

1. 📄 信息弹窗示例
2. ❓ 确认弹窗示例
3. 📋 多选择弹窗示例
4. ⚠️ 警告弹窗示例
5. 🔧 自定义弹窗示例

## 🔧 集成到主应用

在主应用中使用弹出窗口：

```python
class TeamDevApp(App):
    def some_action(self):
        # 确认重要操作
        PopupWinHelper.show_confirm(
            self,
            title="保存项目",
            message="是否保存当前项目的更改？",
            ok_callback=self._save_project,
            cancel_callback=lambda x: None
        )
    
    def _save_project(self, result):
        # 执行保存逻辑
        self.log_panel.add_info("项目已保存", "success")
```

## 📋 注意事项

1. 弹出窗口是模态的，会阻止用户操作其他界面
2. 使用 `app.push_screen(popup)` 显示弹出窗口
3. 回调函数是可选的，可以为 None
4. 选择项的值可以是任何类型（字符串、数字、对象等）
5. 取消按钮可以通过 `show_cancel=False` 隐藏

## 🧪 测试

运行测试脚本验证功能：

```bash
python test_popup_win.py
```

测试包括所有类型的弹出窗口和键盘交互。