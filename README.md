TeamDev 方案概述

(面向本地单用户、多项目、可插拔的多模型系统)

1️⃣ 目标与定位

目标	说明
核心交互	Jim（大型语言模型）负责与用户实时聊天，捕获需求、风险、技术建议。
文档自动化	对话期间，后台使用 更小、更快的模型 将产生的内容写入 PROJ[XXX]-PRD.md（或其它项目文档）。
多角色协作	通过配置可加入 Jacky（架构师）、Happen（开发者）、Fei（数据库专家）、Peipei（测试员） 等“同事”，它们主要是静默执行的任务工具。
多项目管理	同时支持 0~N 个项目，每个项目拥有独立的 PRD、dev‑guide、todo‑list、issue 等文件。
全本地/离线	只要模型本地部署（如 Ollama）或本机 API，所有数据均保存在本地磁盘。
可扩展	新增角色、模型、工具只需编辑配置文件，无需改动核心业务代码。
2️⃣ 系统结构概览

graph LR
    A[用户] -->|对话| B[Jim (大模型)]
    B -->|调用| C[recording模型 (小模型)]
    C -->|写入| D[PROJ-PRD.md]
    B -->|触发| E[Jacky (架构模型)]
    B -->|触发| F[Fei (DB模型)]
    B -->|触发| G[Happen (开发模型)]
    B -->|触发| H[Peipei (测试模型)]
    E -->|更新| I[dev‑guide.md / todo‑list.md]
    G -->|生成| J[代码/commit‑log.md]
    H -->|生成| K[issue‑00x.md]
    style B fill:#ffeb3b,stroke:#333,stroke-width:2px
    style C fill:#90caf9,stroke:#333,stroke-width:2px
    style D fill:#c8e6c9,stroke:#333,stroke-width:2px
    
Jim：唯一与用户交互的角色。
recording模型：速度快、成本低，用来把 Jim 的产出转成 Markdown 并写入文件（异步执行）。
其他角色：在收到任务后静默执行，更新对应文档或产生 Issue。
3️⃣ 关键配置文件

3.1 ai_settings.json – 模型与参数登记

{
  "models": [
    {
      "name": "gpt-4o",
      "type": "chat",
      "api_key": "sk-****",
      "base_url": "https://api.openai.com/v1",
      "temperature": 0.2,
      "role": "conversation",
      "async": false
    },
    {
      "name": "llama3-8b-ollama",
      "type": "chat",
      "base_url": "http://127.0.0.1:11434/api/chat",
      "temperature": 0.5,
      "role": "recording",
      "async": true
    },
    {
      "name": "gemma2-2b",
      "type": "chat",
      "base_url": "http://127.0.0.1:11434/api/chat",
      "temperature": 0.7,
      "role": "archiving",
      "async": true
    }
  ]
}
role：标识模型在系统中的职责（conversation, recording, archiving, analysis …）。
async：true 表示建议使用线程/协程调用，以免阻塞主对话。
3.2 settings-jim.md（以及其他角色的 settings-*.md）

# Jim – 软件开发顾问

**性格**：耐心、善于引导、擅长把抽象需求拆解成可执行的任务。  
**技能**：需求分析、系统设计、技术栈推荐、风险评估。  
**约束**：禁止一次性生成完整 PRD，必须在对话中逐步补全。  
**工作指令**：  
- 当需求完整时，调用 `save_prd` 将 markdown 片段写入 PRD。  
- 如需架构建议，调用 `update_dev_guide` 并让 Jacky 负责。  
...
每个角色拥有自己的系统提示（system prompt）片段，程序在启动时读取并注入模型。
4️⃣ 项目组织（多项目支持）

projects/
├─ 001/
│   ├─ PROJ001-PRD.md
│   ├─ PRD_history/            # 自动备份（时间戳 MD）
│   ├─ dev-guide.md
│   ├─ todo-list.md
│   ├─ issue_history/
│   └─ meta.json                # {"id":"001","name":"移动任务管理","created":"2024-10-01"}
├─ 002/
│   └─ …
└─ …
meta.json 描述项目名称、创建时间等，用于 UI 中的 “Select your project”。
所有工具（save_prd、edit_prd、update_dev_guide …）在内部都通过 当前项目根路径 进行文件读写。
5️⃣ 工作流（文字描述）

用户启动会话 → UI（CLI / Web）提示 “Select your project”。
系统加载对应项目路径，读取 meta.json、settings-jim.md、ai_settings.json。
Jim 使用 conversation 模型 与用户实时交流，利用记忆（摘要+向量检索）保持上下文短小。
当 Jim 判断需求已经充分，系统指示它 调用 save_prd（由 recording 小模型完成）把 简洁的 markdown 追加到 PROJ‑PRD.md。此步骤在 子线程 中执行，不阻塞 与用户的继续对话。
需求触发其他角色：
架构需求 → update_dev_guide → Jacky 的模型更新 dev‑guide.md 与 todo‑list.md。
数据库方案 → update_db_design → Fei 更新 db‑design.md。
实现任务 → assign_task → Happen 开始生成代码，并在完成后把 commit‑log 写入。
测试完成 → run_tests → Peipei 执行测试，如有缺陷生成 issue‑00x.md。
所有写入操作 都在 写前自动备份（复制到对应 *_history/），支持随时回滚。
会话结束（用户输入 exit）后，系统显示当前 PRD 概览并提示是否导出/压缩项目。
6️⃣ 核心技术要点

领域	关键实现	说明
模型统一调度	LLMProvider（读取 ai_settings.json）	把不同供应商、远程或本地模型封装为统一的 generate(messages, **params) 接口。
并发/异步	ThreadPoolExecutor / asyncio + httpx	recording、archiving、角色工具均可在子线程/协程中运行，保证 Jim 对话流畅。
记忆与检索	ConversationSummaryBufferMemory（LangChain） + FAISS 向量库	长对话自动摘要；settings‑jim.md 按块向量化，仅把最相关片段注入系统提示。
工具（Tool）机制	LangChain Tool / OpenAI Functions	save_prd, edit_prd, list_projects, switch_project, update_dev_guide, run_tests 等均以函数形式暴露给模型。
文件/版本管理	文件系统 + 时间戳备份	每次写入前 shutil.copy2 到 *_history/，支持手动或自动回滚。
多项目切换	meta.json + UI（CLI/FastAPI）	“Select your project” 从 projects/ 读取列表，切换后重新实例化记忆和工具。
安全	可选 cryptography.Fernet 加密 PRD、issue 等敏感文件	完全本地运行时不依赖云服务，必要时对磁盘文件加密。
7️⃣ 可插拔扩展方案

新增角色
创建 settings-<role>.md（描述、指令）。
在 ai_settings.json 为该角色添加对应模型（或共享已有模型）。
在工具工厂 注册对应的 Tool（如 update_dev_guide、assign_task）。
替换模型
只需在 ai_settings.json 中修改 base_url、api_key、model_name。
LLMProvider 会自动加载新模型，无需改动业务代码。
任务流改造
将 todo-list.md 迁移为结构化 JSON（id, title, status, assignee），配合轻量任务队列（Celery、RQ）实现真正的 异步任务调度。
8️⃣ 下一步（待确认的细节）

编号	待决事项	备注
①	每个角色对应的 模型名称（大模型 vs 小模型）	确认后在 ai_settings.json 填写。
②	Tool 列表 的完整输入/输出约定	如 save_prd(markdown) -> str，update_dev_guide(section, content) 等。
③	并发实现方式的选型（ThreadPool vs asyncio）	取决于所选模型的调用方式（同步 HTTP 还是异步 gRPC）。
④	文件备份/回滚 的细化策略（保留多少天、是否做 diff）	设计 audit.log 与 history 目录的清理规则。
⑤	系统提示模板（每个角色的 system message）	需要统一的占位符（如 {project_id}）以便在运行时渲染。
⑥	UI 形态：CLI 交互还是轻量 FastAPI 前端？	待讨论后决定后端与前端实现方式。
9️⃣ 结语

本方案已经把 需求 → 角色/模型 → 工具/文件 → 并发执行 的完整链路梳理清晰，并提供了 配置驱动、可插拔、多项目 的实现蓝图。后续只需在 界面 与 细节实现 两大块展开：

界面层（项目选择、会话窗口、文件预览）。
代码层（LLMProvider、ToolFactory、并发调度、持久化）。
一旦界面确定，我们即可进入实现阶段，逐步把上述概念落地为可运行的 Python 包。