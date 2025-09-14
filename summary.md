# Project Summary

## 🎯 项目目标

* 构建一个 **多 Agent 协作系统**，帮助人类用户更高效、完整地澄清需求，避免软件项目失败的根源（需求模糊、矛盾、飘移）。
* 利用 AI 的多角色、跨领域知识，进行 **需求脑暴 + 启发式问答**，最终生成可执行的开发文档。
* 在有了精确的开发指导文档后，调用编码模型输出高质量代码，实现从需求到落地的完整链路。

## 🧩 当前方案演进过程

1. **最初设计**：

   * 使用 TUI（文本界面）来管理多 Agent 对话与需求记录。
   * 将讨论结果存入 markdown (`*.md`) 文件作为需求文档。

2. **局限与反思**：

   * TUI 不直观，流程图等关键交互不便展示。
   * 需求澄清过程需要图形化呈现，单纯文本不足以承载。

3. **方案升级**：

   * 考虑转向 GUI，但带来开发复杂度。
   * 讨论后提出借助 **OpenProject** 替代自建管理层。

4. **关键灵感**：

   * 不再维护独立的 `*.md` 需求记录。
   * 将 AI Agent 的讨论与产出直接写入 OpenProject（任务、文档、Wiki、进度）。
   * 实现 **“AI = 虚拟团队成员”**，人类只需做需求输入与管理。

## 🔧 技术栈选择

* **底层 Agent 框架**：偏向 Autogen（更贴合“多角色头脑风暴”）。
* **任务管理平台**：OpenProject（Ruby on Rails + Angular 前端）。
* **Agent 执行层**：独立服务（Python FastAPI / Node Express），调用 LLM 并通过 OpenProject API 读写数据。
* **可选库参考**：LangChain（工具链整合）、LlamaIndex（后续知识库）、CrewAI（另一种 Agent 协作实现）。

## 📊 系统交互架构

```mermaid
graph TD
    User[👤 人类用户] --> |输入需求/确认| OpenProjectUI[🖥️ OpenProject (Angular UI)]
    
    OpenProjectUI --> |API 调用| AgentGateway[⚡ Agent Gateway (FastAPI/Node)]
    AgentGateway --> |多 Agent 讨论 (Autogen)| LLM[🤖 大模型]

    LLM --> AgentGateway
    AgentGateway --> |产出文档/任务| OpenProjectAPI[(OpenProject REST API)]
    OpenProjectAPI --> |写入需求/任务/文档| DB[(OpenProject DB)]

    OpenProjectUI --> |展示| DB
```

### 说明

* **OpenProject**：保持内核不动，仅在前端 fork/扩展 UI（增加 AI 协作面板）。
* **Agent Gateway**：独立服务，封装多 Agent 协作逻辑，与 OpenProject 解耦。
* **数据闭环**：需求输入 → AI 讨论澄清 → 转换为任务/文档 → 存入 OpenProject → 人类确认/管理。

## ✅ 优势

* 避免重复造轮子（复用 OpenProject 成熟的项目管理能力）。
* 数据全流程闭环，避免 “.md 文件漂移”。
* AI 以“虚拟成员”身份参与项目，行为可审计、可追踪。
* 保持 OpenProject 可升级性，只需维护前端扩展与 Agent Gateway。

## ⚡ 难点

* OpenProject 插件/前端二次开发（Angular 技术栈要求）。
* Agent Gateway 的设计（任务分发、状态追踪、错误恢复）。
* 权限与安全（AI 的任务提交需要人工审批机制）。

---

👉 当前共识：先采用 **外挂模式**（Agent Gateway + OpenProject API），快速验证价值。再逐步嵌入前端，最后实现深度融合。
