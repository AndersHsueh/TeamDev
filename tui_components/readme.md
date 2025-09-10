# TUI 组件库

一个功能丰富的 Python 文本用户界面（TUI）组件库，专为构建现代化的命令行应用程序而设计。

## 特性

- 🎨 **现代化设计** - 支持主题和样式定制
- 🧩 **模块化组件** - 可复用的 UI 组件
- 📱 **响应式布局** - 灵活的布局管理系统
- 🎯 **易于使用** - 简洁的 API 设计
- 🔧 **高度可定制** - 支持自定义主题和样式
- 📊 **丰富组件** - 文件浏览器、编辑器、日志面板等

## 目录结构

```
tui_components/
│
├─ README.md                # 组件库说明文档
│
├─ core/                    # 基础设施（不会直接显示，但给其它组件用）
│   ├─ base_component.py     # 所有组件的基类（定义接口 render(), update() 等）
│   ├─ layout_manager.py     # 布局管理器（负责拼装组件）
│   └─ theme.py              # 颜色/样式定义
│
├─ components/              # 可复用的 TUI 组件
│   ├─ agent_status.py       # Agent 状态显示（头像+状态灯+名称）
│   ├─ file_explorer.py      # 文件浏览树
│   ├─ log_panel.py          # 日志输出窗口
│   ├─ editor.py             # 文本/代码编辑器
│   ├─ project_selector.py   # 项目选择菜单
│   ├─ menu_bar.py           # 顶部/底部菜单栏
│   └─ input_box.py          # 输入框组件
│
├─ examples/                # 示例程序
│   ├─ demo_dashboard.py     # 演示完整界面（文件树 + 编辑器 + Agent 状态 + 日志）
│   └─ demo_agent_status.py  # 单个组件的独立演示
│
└─ tests/                   # 单元测试
    ├─ test_agent_status.py
    ├─ test_file_explorer.py
    └─ test_log_panel.py
```

## 快速开始

### 安装

```bash
# 克隆或下载组件库
git clone <repository-url>
cd tui_components
```

### 基本使用

```python
from core.base_component import BaseComponent
from core.theme import set_theme, Themes
from components.agent_status import AgentStatusComponent, AgentStatus

# 设置主题
set_theme(Themes.get_dark_theme())

# 创建组件
agent = AgentStatusComponent("my_agent")
agent.set_agent_info("Claude", "🤖")
agent.set_status(AgentStatus.WORKING, "处理中...")
agent.set_size(50, 3)

# 渲染组件
print(agent.render())
```

### 完整示例

```python
import sys
import os
sys.path.append('path/to/tui_components')

from examples.demo_dashboard import DashboardApp

# 创建并运行仪表板
app = DashboardApp()
app.set_size(120, 30)
print(app.render())
```

## 组件介绍

### 1. Agent 状态组件 (AgentStatusComponent)

显示 AI 助手的状态信息，包括头像、状态灯和名称。

```python
from components.agent_status import AgentStatusComponent, AgentStatus

agent = AgentStatusComponent("claude")
agent.set_agent_info("Claude", "🤖")
agent.set_status(AgentStatus.THINKING, "分析中...")
agent.set_display_options(
    show_avatar=True,
    show_status_light=True,
    show_name=True,
    show_message=True
)
```

**状态类型：**
- `IDLE` - 空闲（灰色）
- `THINKING` - 思考中（蓝色）
- `WORKING` - 工作中（绿色）
- `ERROR` - 错误（红色）
- `OFFLINE` - 离线（灰色）

### 2. 文件浏览器组件 (FileExplorerComponent)

显示文件系统目录结构，支持导航和选择。

```python
from components.file_explorer import FileExplorerComponent

explorer = FileExplorerComponent("file_explorer")
explorer.set_root_path(".")
explorer.set_file_select_callback(lambda path: print(f"选择了: {path}"))
explorer.set_hidden_files(False)  # 不显示隐藏文件
```

**功能特性：**
- 目录展开/折叠
- 文件选择回调
- 隐藏文件过滤
- 自定义文件过滤器
- 键盘和鼠标导航

### 3. 日志面板组件 (LogPanelComponent)

显示日志消息，支持不同级别的日志和过滤。

```python
from components.log_panel import LogPanelComponent, LogLevel

log_panel = LogPanelComponent("log_panel")
log_panel.add_info("应用程序启动")
log_panel.add_warning("网络连接不稳定")
log_panel.add_error("文件读取失败")
log_panel.set_filter_levels([LogLevel.ERROR, LogLevel.WARNING])
```

**日志级别：**
- `DEBUG` - 调试信息
- `INFO` - 一般信息
- `WARNING` - 警告
- `ERROR` - 错误
- `CRITICAL` - 严重错误

### 4. 编辑器组件 (EditorComponent)

功能丰富的文本/代码编辑器，支持语法高亮和搜索。

```python
from components.editor import EditorComponent

editor = EditorComponent("editor")
editor.set_text("print('Hello, World!')")
editor.set_language("python")
editor.show_line_numbers = True
editor.syntax_highlighting = True
```

**功能特性：**
- 语法高亮（Python、JavaScript 等）
- 行号显示
- 文本搜索和替换
- 选择和高亮
- 键盘快捷键支持

### 5. 项目选择器组件 (ProjectSelectorComponent)

显示项目列表并提供选择功能。

```python
from components.project_selector import ProjectSelectorComponent, Project

selector = ProjectSelectorComponent("project_selector")
project = Project("My Project", "/path/to/project", "Python 项目", "python")
selector.add_project(project)
selector.set_search_text("python")  # 搜索包含 "python" 的项目
```

### 6. 菜单栏组件 (MenuBarComponent)

支持顶部和底部菜单栏，包含菜单项和快捷键。

```python
from components.menu_bar import MenuBarComponent, MenuGroup, MenuItem

menu_bar = MenuBarComponent("main_menu")
file_menu = MenuGroup("File", [
    MenuItem("New", "new", callback, shortcut="Ctrl+N"),
    MenuItem("Open", "open", callback, shortcut="Ctrl+O"),
])
menu_bar.add_menu_group(file_menu)
```

### 7. 输入框组件 (InputBox)

支持用户输入、历史记录和自动换行的输入框组件。

```python
from components.input_box import InputBox

input_box = InputBox(prompt="> ", width=80)
input_box.set_size(80, 3)

# 处理用户输入
result = input_box.handle_key("h")  # 输入字符
result = input_box.handle_key("Enter")  # 提交输入，返回完整字符串
```

**功能特性：**
- 支持提示符显示
- 自动换行处理
- 输入历史记录
- 上下键浏览历史
- 支持中文字符输入
- 回车键提交输入

## 布局管理

使用 `LayoutManager` 来管理组件的布局：

```python
from core.layout_manager import LayoutManager, LayoutType, Alignment

layout = LayoutManager()
layout.set_layout_type(LayoutType.HORIZONTAL)  # 水平布局
layout.set_alignment(Alignment.CENTER)         # 居中对齐
layout.set_spacing(2)                         # 间距
layout.set_padding(1)                         # 内边距

# 应用到容器
layout.layout_components(container, available_rect)
```

**布局类型：**
- `HORIZONTAL` - 水平布局
- `VERTICAL` - 垂直布局
- `GRID` - 网格布局
- `ABSOLUTE` - 绝对定位

## 主题系统

支持多种预定义主题和自定义主题：

```python
from core.theme import set_theme, Themes, Theme

# 使用预定义主题
set_theme(Themes.get_dark_theme())
set_theme(Themes.get_light_theme())
set_theme(Themes.get_monokai_theme())

# 创建自定义主题
custom_theme = Theme("custom")
custom_theme.set_color("primary", "#FF6B6B")
custom_theme.set_color("background", "#2C3E50")
set_theme(custom_theme)
```

**预定义主题：**
- `default` - 默认主题
- `dark` - 深色主题
- `light` - 浅色主题
- `monokai` - Monokai 主题
- `github` - GitHub 主题

## 事件处理

组件支持键盘和鼠标事件处理：

```python
# 键盘事件
def handle_key(self, key: str) -> bool:
    if key == "enter":
        # 处理回车键
        return True
    return False

# 鼠标事件
def handle_mouse(self, x: int, y: int, button: int) -> bool:
    if button == 1:  # 左键
        # 处理左键点击
        return True
    return False
```

## 运行示例

### 完整仪表板演示

```bash
cd tui_components/examples
python demo_dashboard.py
```

### Agent 状态演示

```bash
cd tui_components/examples
python demo_agent_status.py
```

## 运行测试

```bash
cd tui_components/tests
python -m unittest test_agent_status.py
python -m unittest test_file_explorer.py
python -m unittest test_log_panel.py
```

## API 参考

### BaseComponent

所有组件的基类，提供通用接口：

- `render()` - 渲染组件内容
- `update(data)` - 更新组件状态
- `handle_key(key)` - 处理键盘输入
- `handle_mouse(x, y, button)` - 处理鼠标事件
- `set_position(x, y)` - 设置位置
- `set_size(width, height)` - 设置尺寸
- `set_visible(visible)` - 设置可见性

### 布局管理器

- `set_layout_type(type)` - 设置布局类型
- `set_alignment(alignment)` - 设置对齐方式
- `set_spacing(spacing)` - 设置间距
- `set_padding(padding)` - 设置内边距
- `layout_components(container, rect)` - 布局组件

### 主题系统

- `set_theme(theme)` - 设置当前主题
- `get_color(name)` - 获取颜色值
- `get_style(name)` - 获取样式值

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 包含所有核心组件
- 支持主题系统
- 完整的布局管理
- 示例和测试

## 联系方式

如有问题或建议，请提交 Issue 或联系维护者。

---

**注意：** 这是一个演示项目，展示了如何构建一个完整的 TUI 组件库。在实际使用中，您可能需要根据具体需求进行调整和优化。