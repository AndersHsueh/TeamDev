# TeamDev 项目

面向本地单用户、多项目、可插拔的多模型系统

## 🚀 项目状态

- ✅ **TUI 组件库** - 完整的文本用户界面组件库已实现
- ✅ **命令系统** - 基础命令框架已搭建
- ✅ **本地工具接口** - 完整的本地工具接口系统已实现
- 🚧 **核心系统** - 多模型协作系统开发中
- 📋 **UI 界面** - 基于 TUI 组件的用户界面规划中

## 📦 已实现功能

### TUI 组件库 (`tui_components/`)
完整的文本用户界面组件库，包含：

- **核心基础设施**: 组件基类、布局管理器、主题系统
- **7个 TUI 组件**:
  - Agent 状态显示组件
  - 文件浏览器组件
  - 日志面板组件
  - 代码编辑器组件
  - 项目选择器组件
  - 菜单栏组件
  - 输入框组件
- **示例程序**: 完整仪表板演示和单组件演示
- **单元测试**: 完整的测试覆盖

### 命令系统 (`commands/`)
- 基础命令框架
- 命令管理器
- 示例命令实现

### 本地工具接口 (`local-tools/`)
完整的本地工具接口系统，提供安全的系统级操作：

- **6个核心工具**:
  - FileRead - 文件读取工具
  - FileWrite - 文件写入工具
  - FileDelete - 文件删除工具
  - ListDirectory - 目录列举工具
  - ExecuteCommand - 命令执行工具
  - HttpRequest - HTTP 请求工具
- **权限管理系统**: 用户权限验证和路径安全检查
- **统一调度器**: 标准化工具调用接口
- **完整测试覆盖**: 所有工具的单元测试
- **安全特性**: 路径保护、命令过滤、网络安全防护

## 🛠️ 快速开始

```bash
# 克隆项目
git clone <repository-url>
cd TeamDev

# 安装依赖
pip install -r requirements.txt

# 运行 TUI 组件库演示
cd tui_components/examples
python demo_dashboard.py
```

## 📚 文档

- [本地工具接口文档](./local-tools/README.md) - 工具接口使用指南
- [TUI 组件库文档](./tui_components/README.md) - 详细的组件使用指南
- [项目概述](#teamdev-方案概述) - 系统架构和设计理念

## 📁 项目结构

```
TeamDev/
├─ README.md                    # 项目说明文档
├─ requirements.txt             # 项目依赖
├─ .gitignore                   # Git 忽略规则
├─ local-tools/                 # 本地工具接口
│   ├─ tools/                   # 工具实现
│   │   ├─ file_read.py         # 文件读取工具
│   │   ├─ file_write.py        # 文件写入工具
│   │   ├─ execute_command.py   # 命令执行工具
│   │   └─ *.py                 # 其他工具
│   ├─ permissions/             # 权限管理
│   │   └─ permission_manager.py
│   ├─ tests/                   # 单元测试
│   ├─ tool_runner.py           # 统一调度器
│   └─ README.md                # 工具接口文档
├─ commands/                    # 命令系统
│   ├─ command_base.py          # 命令基类
│   ├─ command_manager.py       # 命令管理器
│   └─ *.py                     # 各种命令实现
├─ tui_components/              # TUI 组件库
│   ├─ core/                    # 核心基础设施
│   ├─ components/              # TUI 组件
│   ├─ examples/                # 示例程序
│   ├─ tests/                   # 单元测试
│   └─ README.md                # 组件库文档
└─ projects/                    # 项目存储目录（规划中）
    └─ 001/                     # 项目示例
        ├─ PROJ001-PRD.md
        ├─ dev-guide.md
        └─ meta.json
```

---

# TeamDev 方案概述

## 1️⃣ 目标与定位

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
8️⃣ 下一步开发计划

### 已完成 ✅
- [x] TUI 组件库基础架构
- [x] 7个核心 TUI 组件
- [x] 命令系统框架
- [x] 本地工具接口系统
- [x] 6个核心工具实现
- [x] 权限管理系统
- [x] 统一工具调度器
- [x] 完整测试覆盖
- [x] 项目文档和依赖管理

### 进行中 🚧
- [ ] 多模型协作系统核心实现
- [ ] LLMProvider 统一模型接口
- [ ] 项目管理系统
- [ ] 基于 TUI 的主界面

### 待开发 📋
编号	待决事项	优先级	备注
①	LLMProvider 实现	高	统一不同模型的调用接口
②	角色系统实现	高	Jim、Jacky、Happen 等角色的具体实现
③	工具系统集成	中	将 TUI 组件与工具系统结合
④	项目文件管理	中	PRD、dev-guide 等文件的自动生成和管理
⑤	记忆和检索系统	中	对话记忆和向量检索功能
⑥	配置文件系统	低	ai_settings.json 和角色配置的完整实现
9️⃣ 结语

本方案已经把 需求 → 角色/模型 → 工具/文件 → 并发执行 的完整链路梳理清晰，并提供了 配置驱动、可插拔、多项目 的实现蓝图。

### 当前进展
- ✅ **界面层基础** - TUI 组件库已完成，提供了丰富的用户界面组件
- ✅ **命令系统** - 基础命令框架已搭建，支持可扩展的命令管理
- 🚧 **核心系统** - 正在实现多模型协作和项目管理功能

### 下一步重点
1. **LLMProvider 实现** - 统一不同 AI 模型的调用接口
2. **角色系统** - 实现 Jim、Jacky、Happen 等角色的具体功能
3. **系统集成** - 将 TUI 组件与核心系统结合，形成完整的用户界面

项目已具备坚实的基础架构，可以逐步将概念落地为可运行的 Python 应用程序。