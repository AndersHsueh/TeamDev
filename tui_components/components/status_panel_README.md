# StatusPanel 组件功能说明

## 概述
`StatusPanelComponent` 是一个位于界面底部的状态栏组件，用于显示系统状态、提示信息、快捷键说明等。根据原型图设计，它位于输入框下方，为用户提供实时的状态反馈。

## 文件位置
- 组件文件: `tui_components/components/status_panel.py`
- 测试文件: `tui_components/tests/test_status_panel.py`

## 主要功能

### 1. 状态类型支持
- `NORMAL` - 普通状态信息
- `SUCCESS` - 成功状态（✅）
- `WARNING` - 警告状态（⚠️）
- `ERROR` - 错误状态（❌）
- `INFO` - 提示信息（ℹ️）
- `HELP` - 帮助信息（💡）

### 2. 消息管理
- **StatusMessage类**: 封装状态消息的数据结构
- **自动清除**: 支持设置消息自动过期时间
- **图标显示**: 根据状态类型显示对应图标
- **时间戳**: 记录消息创建时间

### 3. 永久信息显示
- 支持添加永久显示的信息（如快捷键提示）
- 可动态添加/移除永久信息
- 与临时状态消息并行显示

## 核心方法

### 基本状态设置
```python
# 设置不同类型的状态
status_panel.set_success("操作成功", auto_clear=True)
status_panel.set_warning("注意事项")
status_panel.set_error("发生错误")
status_panel.set_info("提示信息")
status_panel.set_help("帮助内容")
```

### 预设状态
```python
# 常用状态快捷方法
status_panel.show_ready()          # 显示就绪状态
status_panel.show_busy("加载中")    # 显示忙碌状态
status_panel.show_shortcuts()      # 显示快捷键信息
```

### 永久信息管理
```python
# 添加快捷键提示
status_panel.add_permanent_info("Ctrl+Q", "退出")
status_panel.add_permanent_info("Ctrl+S", "保存")

# 移除特定信息
status_panel.remove_permanent_info("Ctrl+S")

# 清除所有永久信息
status_panel.clear_permanent_info()
```

## 在主应用中的集成

### 1. 导入和初始化
```python
from tui_components.components.status_panel import StatusPanelComponent

# 在 __init__ 中创建
self.status_panel = StatusPanelComponent(
    id="status_panel", 
    default_message="TeamDev 就绪"
)
```

### 2. CSS样式配置
```css
#status_panel {
    height: 1;                    /* 固定高度 */
    background: $accent-darken-3;  /* 背景色 */
    color: $text;                 /* 文字色 */
    padding: 0 1;                 /* 内边距 */
}
```

### 3. 界面布局
```python
def compose(self) -> ComposeResult:
    yield self.title_bar     # 顶部标题
    yield self.log_panel     # 中部日志
    yield self.input_box     # 输入框
    yield self.status_panel  # 底部状态栏
```

## 使用示例

### 命令反馈
```python
# 在命令处理中提供状态反馈
async def on_input_box_component_submitted(self, event):
    text = event.value.strip()
    
    if text == "/help":
        # 显示帮助命令
        self.log_panel.add_info("帮助信息...", "help")
        self.status_panel.set_success("帮助信息已显示", auto_clear=True)
    
    elif text == "/clear":
        # 清空对话
        self.log_panel.clear_logs()
        self.status_panel.set_success("对话已清空", auto_clear=True)
```

### 长时间操作
```python
# 显示处理状态
async def process_long_task(self):
    self.status_panel.show_busy("正在处理")
    # ... 执行长时间任务 ...
    self.status_panel.set_success("处理完成", auto_clear=True)
```

### 初始化设置
```python
def on_mount(self) -> None:
    # 设置初始状态和快捷键提示
    self.status_panel.show_shortcuts()
    self.status_panel.set_info("欢迎使用 TeamDev！")
```

## 技术特性

### 1. 响应式渲染
- 自动适应容器宽度
- 内容过长时自动截断并显示省略号
- 支持多部分信息的分隔符显示

### 2. 自动过期机制
- 支持消息自动清除
- 可配置过期时间
- 在update()调用时检查和清理过期消息

### 3. 兼容性
- 支持Python 3.8+的类型注解
- 继承自BaseComponent基类
- 遵循Textual框架规范

## 界面效果

状态栏位于界面最底部，显示格式如下：
```
[状态信息] | [永久信息1] | [永久信息2] | ...
```

示例显示：
```
✅ 操作成功 | Ctrl+Q: 退出 | Ctrl+T: 切换主题 | /help: 帮助
```

## 总结

StatusPanel组件成功补充了TUI界面的底部状态栏功能，提供了：
- ✅ 丰富的状态类型和图标支持
- ✅ 自动过期的临时消息机制  
- ✅ 永久信息显示（快捷键等）
- ✅ 与主应用的完整集成
- ✅ 响应式渲染和用户体验优化

该组件填补了原型图中状态栏的功能缺失，为用户提供了清晰的状态反馈和操作指导。