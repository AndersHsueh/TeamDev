"""
项目文档 schema 定义
定义各种文档的数据结构和验证规则
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectMeta:
    """项目元信息"""
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    status: str = "active"
    version: str = "1.0.0"
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "version": self.version,
            "tags": self.tags or []
        }


@dataclass
class PRDSection:
    """PRD 文档章节"""
    title: str
    content: str
    order: int = 0
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "content": self.content,
            "order": self.order,
            "updated_at": self.updated_at or datetime.now().isoformat()
        }


@dataclass
class TodoItem:
    """待办事项"""
    id: str
    title: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    assignee: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due_date": self.due_date,
            "tags": self.tags or []
        }


@dataclass
class Issue:
    """问题/缺陷"""
    id: str
    title: str
    description: str
    severity: str = "medium"  # low, medium, high, critical
    status: str = "open"  # open, in_progress, resolved, closed
    reporter: str = ""
    assignee: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    resolved_at: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "reporter": self.reporter,
            "assignee": self.assignee,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "tags": self.tags or []
        }


# 文档模板
PRD_TEMPLATE = """# 产品需求文档 (PRD)

## 项目概述
[项目基本信息、目标用户、核心价值]

## 功能需求

### 核心功能
1. [功能描述]
2. [功能描述]

### 次要功能
1. [功能描述]
2. [功能描述]

## 非功能需求

### 性能需求
- [性能指标]

### 安全需求
- [安全要求]

### 用户体验
- [UX 要求]

## 验收标准
- [验收条件]

---
*生成时间: {timestamp}*
"""

DEV_GUIDE_TEMPLATE = """# 开发指南

## 项目架构
[系统架构图和技术栈说明]

## 开发环境
[环境配置和依赖说明]

## 代码规范
[编码规范和最佳实践]

## 部署说明
[部署流程和配置]

---
*生成时间: {timestamp}*
"""

PROJECT_INFO_TEMPLATE = """# {project_name}

## 项目基本信息

- **项目ID**: `{project_id}`
- **项目名称**: {project_name}
- **项目描述**: {description}
- **创建时间**: {created_at}
- **项目状态**: {status}
- **项目版本**: {version}

## 总纲要 Todo 列表

### 🔴 P0 - 核心功能 (必须完成)
- [ ] 需求分析和功能设计
- [ ] 系统架构设计
- [ ] 核心功能开发
- [ ] 基础测试

### 🟠 P1 - 重要功能 (建议完成)
- [ ] 用户界面开发
- [ ] 数据库设计和实现
- [ ] API 接口开发
- [ ] 文档编写

### 🟡 P2 - 扩展功能 (可选)
- [ ] 性能优化
- [ ] 高级功能开发
- [ ] 部署和运维
- [ ] 用户培训

## 项目进度统计

- **总任务数**: 12
- **已完成**: 0
- **进行中**: 0
- **待开始**: 12
- **完成率**: 0%

---
*此文档由 TeamDev 自动生成*
"""

README_TEMPLATE = """# {project_name}

{description}

## 快速开始

### 环境要求
- Python 3.8+
- [其他依赖]

### 安装步骤
```bash
# 安装依赖
pip install -r requirements.txt

# 运行项目
python main.py
```

## 项目结构
- `src/` - 源代码
- `tests/` - 测试文件
- `docs/` - 文档
- `config/` - 配置文件

## 开发团队
- 项目经理: [姓名]
- 技术负责人: [姓名]
- 开发团队: [成员列表]

---
*此文档由 TeamDev 自动生成*
"""
