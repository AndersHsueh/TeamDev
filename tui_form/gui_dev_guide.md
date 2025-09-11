 GUI Dev Guide — `gui_form/gui_dev_guide.md`（初稿）

> 目的：为能让代码生成器（比如 `grok-code-fast-1`）可靠、可复用地**生成/修改 TUI 界面 JSON**，并由 `LayoutManager` 在运行时解析绘制界面，给出一份严格、可验证、带示例的开发说明。  
> 要求：生成的 JSON **只描述界面**（布局 + 组件 + 初始数据 + 事件映射），**不得修改组件实现**。组件实现由 `tui_components/components/*` 提供并维护。

---

## 1. 总体约定（must-follow rules for grok）
1. **只生成/修改 JSON** 文件（例如 `mainform.json`、`modal_X.json`），不改组件源码。  
2. JSON 中使用的组件名必须与 `components` 目录中导出的类名精确匹配（大小写一致）。  
3. 每个组件节点必须含有 `type`（必须）、`id`（必须且唯一）、如果是可视组件则需包含 `component` 字段指向组件名。  
4. 布局单位：  
   - 宽度/高度可以是整数百分比（例如 `width: 20` 表示 20% 宽度）或绝对数（例如 `width: 30` 表示 30 列字符）。  
   - 组件接收 `height` 或 `width` 时，如果为 0 或未指定，表示“自动填充”。  
5. `id` 为全局唯一字符串（字母/数字/下划线）。不要用空格或特殊字符。  
6. 事件/动作字段请使用 `actions`（见第 6 节）。不要直接把逻辑写到 JSON。  
7. 对于可动态扩展的数组（例如 `task_list` 的 `items`），请使用标准数组对象：每项包含被组件识别的字段（例如 `id`, `title`, `status`）。  
8. 生成 JSON 后，请运行 `python gui_form/ui_editor.py gui_form/mainform.json` 做本地预览（见第 9 节）。

---

## 2. JSON 顶层 schema（简化版）
每个 form JSON 顶层为一个 `form` 对象，包含 `name`, `type`, `title`, `layout`，`children`。

示例（结构）：
```json
{
  "name": "mainform",
  "type": "form",
  "title": "TeamDev, Current Project: [XXX]",
  "layout": "vertical",
  "children": [
    { ... },   // header
    { ... },   // split area (agent list / work area / task list)
    { ... },   // input_box
    { ... }    // status_bar
  ]
}
```

`layout` 支持（至少）：
- `"vertical"`：垂直堆叠 children
- `"horizontal"`：水平并列 children
- `"split"`（direction 字段控制水平/垂直，见示例）

---

## 3. 常用组件字段约定（组件化规范）

### 公共字段（每个节点）
- `type`：`panel` / `split` / `form` / `modal` 等（字符串，必需）。
- `id`：唯一 id（字符串，必需）。
- `component`：组件名（例如 `AgentList`、`InputBox` 等）。对于纯布局容器可不写。
- `width` / `height`：整数（% 或字符列数，见第1节）。
- `scroll`：`"vertical"` / `"horizontal"` / `"both"` / `null`
- `data`：初始数据对象（可选）
- `actions`：事件映射（可选，详见第 6 节）
- `style`：样式提示（颜色名称、简易属性，说明性，渲染器可选择性实现）

### InputBox（必填约定）
```json
{
  "type": "panel",
  "id": "input_box",
  "component": "InputBox",
  "height": 3,
  "data": {
    "prompt": "> ",
    "placeholder": "Type your message or /command",
    "history_limit": 200
  },
  "actions": {
    "on_submit": { "command": "send_message" },
    "on_command": { "command": "command_exec" }
  }
}
```

### AgentList
```json
{
  "type": "panel",
  "id": "agent_list",
  "component": "AgentList",
  "width": 20,
  "data": {
    "agents": [
      {"id":"jim","name":"Jim","role":"Product","status":"active","color":"green"},
      {"id":"jacky","name":"Jacky","role":"Architect","status":"active","color":"green"},
      {"id":"ada","name":"Ada","role":"Test Engg.","status":"idle","color":"gray"}
    ]
  }
}
```

### WorkArea（主滚动输出区）
```json
{
  "type": "panel",
  "id": "work_area",
  "component": "WorkArea",
  "scroll": "vertical",
  "data": {
    "lines": ["[Agent Jim] Started analysis...", "You: please create MVP"]
  }
}
```

### TaskList
```json
{
  "type": "panel",
  "id": "task_list",
  "component": "TaskList",
  "width": 25,
  "data": {
    "items": [
      {"step":1,"agent":"Jacky","status":"done","title":"Design API","id":"t1"},
      {"step":2,"agent":"Ada","status":"error","title":"Test cases","id":"t2"},
      {"step":3,"agent":"Jim","status":"working","title":"Draft PRD","id":"t3"}
    ]
  }
}
```

### StatusBar（单行）
```json
{
  "type": "panel",
  "id": "status_bar",
  "height": 1,
  "component": "StatusBar",
  "data": {
    "text": "Main Model: grok-code-fast-1"
  }
}
```

---

## 4. Modal / 子窗体 示例
```json
{
  "name": "confirm_save",
  "type": "modal",
  "title": "Confirm Save",
  "width": 50,
  "height": 7,
  "children": [
    {
      "type":"panel",
      "id":"confirm_text",
      "content":"Are you sure to save current progress?"
    },
    {
      "type":"panel",
      "id":"confirm_buttons",
      "component":"ActionButtons",
      "data":{"buttons":[{"label":"Yes","action":{"command":"confirm_save_yes"}},{"label":"No","action":{"command":"confirm_save_no"}}]}
    }
  ]
}
```

---

## 5. 如何增加新组件（给 grok 一套明确步骤）
1. 先尝试用已有组件组合实现 UI（避免新增组件）。  
2. 若确实需要新组件：  
   - `tui_components/components/<NewComponent>.py`：组件骨架（遵守 BaseComponent 接口，见第 7 节）。  
   - 更新 `tui_components/components/__init__.py` 导出新组件名。  
   - 新的 JSON 可以引用 `component: "NewComponent"`。  

---

## 6. Actions / 事件映射（如何在 JSON 中绑定行为）
```json
"actions": {
  "on_submit": {"type":"command", "name":"send_message", "args_from":"value"},
  "on_click": {"type":"command", "name":"open_file", "args": {"path":"projects/001/README.md"}}
}
```

---

## 7. 组件基类接口
```python
class BaseComponent:
    def __init__(self, id: str):
        self.id = id

    def render(self, width: int, height: int) -> List[str]:
        raise NotImplementedError

    def update(self, data: dict) -> None:
        raise NotImplementedError

    def handle_event(self, event: dict) -> dict:
        raise NotImplementedError
```
---

## 8. JSON 验证（建议脚本）
```python
import jsonschema, json
schema = {...}
def validate(path):
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    jsonschema.validate(instance=data, schema=schema)
```

---

## 9. 本地预览工具：`ui_editor.py`
```bash
python gui_form/ui_editor.py gui_form/mainform.json
```

---

## 10. 示例：完整 `mainform.json`
```json
{
  "name": "mainform",
  "type": "form",
  "title": "TeamDev, Current Project: [XXX]",
  "layout": "vertical",
  "children": [
    {"type":"panel","id":"header","height":1,"content":"TeamDev, Current Project: [XXX]"},
    {
      "type":"split",
      "direction":"horizontal",
      "children":[
        {"type":"panel","id":"agent_list","width":20,"component":"AgentList","data":{"agents":[{"id":"jim","name":"Jim","role":"Product","status":"active","color":"green"},{"id":"jacky","name":"Jacky","role":"Architect","status":"active","color":"green"},{"id":"ada","name":"Ada","role":"Test Engg.","status":"idle","color":"gray"}]}},
        {"type":"panel","id":"work_area","component":"WorkArea","scroll":"vertical","data":{"lines":[]}},
        {"type":"panel","id":"task_list","width":25,"component":"TaskList","data":{"items":[{"step":1,"agent":"Jacky","status":"done","title":"Design API","id":"t1"},{"step":2,"agent":"Ada","status":"error","title":"Test cases","id":"t2"},{"step":3,"agent":"Jim","status":"working","title":"Draft PRD","id":"t3"}]} }
      ]
    },
    {"type":"panel","id":"input_box","component":"InputBox","height":3,"data":{"prompt":"> ","placeholder":"Type or /command","history_limit":200},"actions":{"on_submit":{"type":"command","name":"send_message","args_from":"value"},"on_command":{"type":"command","name":"command_exec","args_from":"value"}}},
    {"type":"panel","id":"status_bar","height":1,"component":"StatusBar","data":{"text":"Main Model: grok-code-fast-1"}}
  ]
}
```

---

## 11. 调试与常见问题
- 缺少组件类 → `ui_editor` 会报错。  
- 字段类型错误 → `width`/`height` 必须为整数。  
- 事件未触发 → 检查 `actions` 的 `type/name`。  
- 渲染越界 → 终端太小时，LayoutManager 应降级处理。

---

## 12. 最佳实践（给 grok 的写法模板）
- 修改/生成 JSON，**不要改 `components/*.py`**。  
- JSON 文件名用 snake_case。  
- 每次变更后运行 `validate_form.py` 和 `ui_editor.py`。  
- 新组件 → 先写骨架，再 JSON。  
- 写注释：在同目录下放置 `*.notes.md`。

---

## 13. 版本与变更记录
- 初稿（v0.1）。后续加入 JSON Schema 与 `LayoutManager` 文档。
