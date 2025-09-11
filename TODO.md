# TODO — 明日任务清单

## 1. JSON 可靠性工具
- [ ] 写一个 `validate_form.py`
  - 功能：检查 JSON 是否符合基本规范（必有 `id`、`type`、`component` 等字段）
  - 检查是否有 **重复 id**
  - 检查 `children` 字段是否数组
  - 输出验证结果（OK 或错误信息）

## 2. 输入框交互增强
- [ ] 在 `InputBox` 里实现命令/普通输入的区分
  - 如果输入以 `/` 开头，交给 **CommandManager**
  - 否则当作普通对话
- [ ] 为 `/save` 加上 **确认流程**：输入 `y/n` 后才真正执行

## 3. 增加一个 Modal 示例
- [ ] 写一个 `confirm_modal.json`（比如保存时弹出确认窗口）
- [ ] 用 `ui_editor.py confirm_modal.json` 测试能否渲染
- [ ] 在 `InputBox` 输入 `/save` 时触发调用 modal

## 4. 文档完善
- [ ] 在 `gui_dev_guide.md` 增加 **“如何写 modal”** 的简短实例
- [ ] 在 `commands/README.md` 写一份简要命令清单

---

✅ 完成这些，你的系统就能做到：
1. JSON 界面可验证
2. 命令能安全执行
3. 支持弹窗（modal）
4. 有文档，groks 能继续帮忙自动扩展
