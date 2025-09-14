# TeamDev - AI团队协作开发平台

TeamDev是一个基于多Agent协作的软件开发平台，旨在通过AI团队的协同工作来自动化软件开发流程。

## 🎯 最新功能 (v2025.09.15)

### ✨ 项目状态管理系统
- **智能项目选择**: 系统启动时自动弹出项目选择对话框
- **状态持久化**: 自动保存和恢复项目状态，支持工作会话恢复
- **可扩展配置**: 支持项目配置、LLM设置、工作状态等扩展信息
- **全局状态管理**: 单例模式的项目状态管理器，确保状态一致性

### 📊 智能日志系统
- **按小时轮转**: 自动生成 `log-YYYY-MM-DD-HH.log` 格式的日志文件
- **多级别支持**: DEBUG、INFO、WARNING、ERROR、CRITICAL 完整日志级别
- **自动清理**: 支持按天数自动清理旧日志文件
- **性能优化**: 高效的日志处理和文件轮转机制

### 🔧 增强的命令系统
- **`/project`** (简写 `/p`): 完整的项目管理命令
- **`/switch`** (简写 `/s`): 快速项目切换功能
- **智能帮助**: 集成的命令帮助和使用指南
- **交互式界面**: 支持 TUI 和命令行双重交互方式

## 项目架构

```mermaid
graph TD
    A[用户] --> B[TeamDev CLI/TUI]
    B --> C[ProjectManager]
    C --> D[Agent Router]
    D --> E[Monica<br/>需求分析员]
    D --> F[Jacky<br/>架构师]
    D --> G[Happen<br/>全栈工程师]
    D --> H[Fei<br/>数据库专家]
    D --> I[Peipei<br/>测试工程师]
    E --> J[LLM API]
    F --> J
    G --> J
    H --> J
    I --> J
```

## 角色系统

TeamDev包含以下AI角色：

- **Monica (需求分析员/产品经理)** - 负责与用户交互，收集需求，进行需求分析，并将任务分配给其他角色
- **Jacky (架构师)** - 负责系统架构设计和技术选型
- **Happen (全栈工程师)** - 负责前后端代码实现
- **Fei (数据库专家)** - 负责数据库设计和优化
- **Peipei (测试工程师)** - 负责测试用例设计和质量保证

## 项目结构

```
TeamDev/
├── core/                    # 核心模块
│   ├── __init__.py
│   ├── logging_system.py   # 智能日志系统 (新增)
│   ├── llm_provider/        # LLM服务提供商集成
│   │   ├── __init__.py
│   │   ├── base.py          # 抽象基类和数据结构
│   │   ├── factory.py       # 工厂模式实现
│   │   ├── openai_provider.py    # OpenAI API集成
│   │   ├── ollama_provider.py    # Ollama本地模型集成
│   │   ├── lmstudio_provider.py  # LMStudio本地模型集成
│   │   └── mock_provider.py      # 测试模拟实现
│   ├── roles/               # Agent角色实现
│   │   ├── __init__.py
│   │   ├── base_role.py     # 基础角色类
│   │   ├── monica.py        # 需求分析员角色
│   │   ├── jacky.py         # 架构师角色
│   │   ├── happen.py        # 全栈工程师角色
│   │   ├── fei.py           # 数据库专家角色
│   │   └── peipei.py        # 测试工程师角色
│   └── project_manager/     # 项目管理器 (重大更新)
│       ├── __init__.py
│       ├── manager.py       # 项目管理核心逻辑
│       ├── api.py           # 项目管理API接口
│       ├── project_state.py     # 项目状态管理 (新增)
│       ├── project_selector.py  # 项目选择器 (新增)
│       ├── file_ops.py      # 文件操作
│       ├── history.py       # 历史管理
│       └── schema.py        # 数据模型
├── commands/                # 命令系统 (增强)
│   ├── __init__.py          # 命令系统初始化 (新增)
│   ├── command_base.py      # 命令基类
│   ├── command_manager.py   # 命令管理器
│   ├── help_command.py      # 帮助命令
│   ├── project_command.py   # 项目管理命令 (新增)
│   ├── switch_command.py    # 项目切换命令 (更新)
│   ├── save_command.py      # 保存命令
│   └── load_command.py      # 加载命令
├── logs/                    # 日志目录 (新增)
│   └── log-YYYY-MM-DD-HH.log # 按小时轮转的日志文件
├── user-documents/          # 用户项目目录
├── tui_components/          # TUI界面组件
│   ├── components/          # 各种UI组件实现
│   ├── core/               # TUI核心模块
│   └── examples/           # 组件使用示例
├── tui_form/                # TUI界面配置
│   ├── mainform.json        # 主界面配置
│   └── gui_dev_guide.md     # GUI开发指南
├── test_project_system.py   # 项目系统测试 (新增)
├── ai_settings.json         # AI模型配置文件
├── agents-config.md         # Agent配置文件
├── requirements.txt         # 项目依赖
└── README.md
```
│   │   ├── monica.py        # 需求分析员角色
│   │   ├── jacky.py         # 架构师角色
│   │   ├── happen.py        # 全栈工程师角色
│   │   ├── fei.py           # 数据库专家角色
│   │   └── peipei.py        # 测试工程师角色
│   └── project_manager/     # 项目管理器
│       ├── __init__.py
│       ├── manager.py       # 项目管理核心逻辑
│       └── api.py           # 项目管理API接口
├── tui_components/          # TUI界面组件
│   ├── components/          # 各种UI组件实现
│   ├── core/               # TUI核心模块
│   └── examples/           # 组件使用示例
├── tui_form/                # TUI界面配置
│   ├── mainform.json        # 主界面配置
│   └── gui_dev_guide.md     # GUI开发指南
├── ai_settings.json         # AI模型配置文件
├── agents-config.md         # Agent配置文件
├── requirements.txt         # 项目依赖
└── README.md
```

## LLM 服务支持

TeamDev 支持多种 LLM 服务提供商，通过统一的抽象接口实现无缝切换：

### 支持的服务商

1. **OpenAI API** - 支持 GPT-4、GPT-3.5 等模型
2. **Ollama** - 本地部署的开源模型 (Llama、Mistral 等)
3. **LMStudio** - 本地图形化模型管理和部署
4. **Mock Provider** - 测试和开发用模拟实现

### LMStudio 集成

LMStudio 是一个本地化的 AI 模型管理平台，TeamDev 现已完全支持：

**特点：**
- 🔒 **完全本地化** - 数据不出本地环境，保障隐私安全
- 🎯 **图形界面** - 通过友好的界面管理模型下载和运行
- ⚡ **即插即用** - 兼容 OpenAI API 格式，无需额外配置
- 🚀 **高性能** - 原生优化，支持 GPU 加速

**配置示例：**
```json
{
  "name": "lmstudio-local",
  "type": "lmstudio",
  "base_url": "http://127.0.0.1:1234",
  "model_name": "your-model-name",
  "temperature": 0.7
}
```

## 安装和使用

### 环境要求

- Python 3.9+
- pip包管理器
- LMStudio (推荐) 或其他支持的 LLM 服务

### 安装步骤

1. 克隆项目仓库：
   ```bash
   git clone <repository-url>
   cd TeamDev
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 LLM 服务：
   - **使用 LMStudio (推荐)**：
     1. 下载并安装 LMStudio
     2. 启动 LMStudio 并加载模型
     3. 确保服务运行在 http://127.0.0.1:1234
   
   - **其他服务**：
     编辑 `ai_settings.json` 配置您的 API 密钥和服务地址

4. 运行项目：
   ```bash
   python main.py
   ```
   
   **首次运行时，系统会自动弹出项目选择对话框：**
   - 可以选择现有项目
   - 也可以创建新项目
   - 项目状态会自动保存和恢复

### 🎮 使用指南

#### 项目管理命令
- **`/project`** 或 **`/p`** - 查看当前项目信息、列出所有项目
- **`/switch`** 或 **`/s`** - 切换到其他项目
- **`/help`** - 显示所有可用命令

#### 日志查看
- 日志文件位于 `./logs/` 目录
- 格式：`log-YYYY-MM-DD-HH.log`
- 按小时自动轮转，支持自动清理

#### 项目状态
- 项目状态自动保存到 `~/.teamdev/current_project.json`
- 支持工作会话恢复
- 可扩展的项目配置和元数据

## 开发指南

### 新功能测试

项目包含完整的测试系统：

```bash
# 运行项目系统测试
python test_project_system.py
```

测试覆盖：
- ✅ 日志系统功能和轮转
- ✅ 项目状态管理和持久化
- ✅ 项目选择器功能
- ✅ 命令系统集成
- ✅ 整体功能集成测试

### 项目状态管理

项目状态管理系统提供：
- **`ProjectInfo`** - 可扩展的项目信息容器
- **`ProjectStateManager`** - 单例模式的全局状态管理
- **`ProjectSelector`** - 项目选择和创建功能
- **自动持久化** - 状态自动保存到用户目录

### 日志系统

智能日志系统特性：
- **按小时轮转** - 自动生成时间戳日志文件
- **多级别支持** - 完整的日志级别体系
- **自动清理** - 可配置的日志保留策略
- **性能优化** - 高效的文件处理和内存管理

### 添加新角色

1. 在 `core/roles/` 目录下创建新的角色文件
2. 继承 `BaseRole` 类并实现必要的方法
3. 在 `core/roles/__init__.py` 中导出新角色
4. 在 `core/__init__.py` 的 `__all__` 列表中添加新角色
5. 更新 `agents-config.md` 添加新角色的配置

### 项目管理

项目管理功能现在包括：
- **智能项目发现** - 自动扫描和识别项目
- **状态持久化** - 工作状态自动保存和恢复
- **配置管理** - 灵活的项目配置系统
- **扩展支持** - 支持自定义扩展字段

### 界面开发

TUI界面配置存储在 `tui_form/` 目录中：
- `mainform.json` 定义主界面布局
- `gui_dev_guide.md` 提供界面开发指南

## 配置说明

Agent的配置信息存储在 `agents-config.md` 文件中，包含：
- 每个Agent的角色定义和能力描述
- 使用的LLM模型配置
- Agent间协作流程图

## 📚 更新日志

### v2025.09.15 (DEV-20250915-C2)
- ✨ **新增项目状态管理系统** - 支持智能项目选择和状态持久化
- ✨ **新增智能日志系统** - 支持按小时轮转和自动清理
- 🔧 **增强命令系统** - 添加 `/project` 和 `/switch` 命令
- 🔧 **改进主程序入口** - 集成项目选择器和状态管理
- 📊 **完整测试覆盖** - 添加项目系统集成测试
- 📖 **文档更新** - 更新 README 和开发指南

### 主要改进
- **用户体验提升** - 启动时自动项目选择，状态自动恢复
- **开发效率提升** - 智能日志系统，便于调试和监控
- **系统稳定性提升** - 完善的错误处理和状态管理
- **可扩展性提升** - 模块化设计，支持未来功能扩展

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。