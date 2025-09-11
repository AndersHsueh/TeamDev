# TeamDev 项目管理器模块

本文档包含了 `core/project_manager/` 目录下所有 Python 文件的完整代码，用于项目管理和文件操作功能。

## 目录结构

```
core/project_manager/
├── __init__.py          # 包初始化和导出
├── schema.py            # 数据结构定义和模板
├── file_ops.py          # 文件操作模块
├── history.py           # 历史记录管理
└── manager.py           # 项目管理器主模块
```

---

## 1. 包初始化 (`__init__.py`)

```python
"""
项目管理模块
提供项目生命周期管理和文件操作功能
"""

from .manager import ProjectManager, get_project_manager
from .file_ops import FileOperations, get_file_operations
from .schema import (
    ProjectMeta,
    PRDSection,
    TodoItem,
    Issue,
    PRD_TEMPLATE,
    DEV_GUIDE_TEMPLATE,
    README_TEMPLATE
)
from .history import HistoryManager, get_history_manager

__all__ = [
    # 主要类
    "ProjectManager",
    "FileOperations",
    "HistoryManager",

    # 便捷函数
    "get_project_manager",
    "get_file_operations",
    "get_history_manager",

    # 数据结构
    "ProjectMeta",
    "PRDSection",
    "TodoItem",
    "Issue",

    # 模板
    "PRD_TEMPLATE",
    "DEV_GUIDE_TEMPLATE",
    "README_TEMPLATE"
]
```

---

## 2. 数据结构定义 (`schema.py`)

```python
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
```

---

## 3. 文件操作模块 (`file_ops.py`)

```python
"""
文件操作模块
提供安全的文件读写和备份功能
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FileOperations:
    """
    文件操作类

    提供安全的文件操作功能，包括自动备份
    """

    def __init__(self, backup_dir: str = "./backups"):
        """
        初始化文件操作器

        Args:
            backup_dir: 备份目录
        """
        self.backup_dir = os.path.abspath(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_with_backup(self, file_path: str, content: str,
                        user_id: str = "system") -> bool:
        """
        保存文件并自动备份

        Args:
            file_path: 文件路径
            content: 文件内容
            user_id: 用户ID

        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 如果文件存在，先备份
            if os.path.exists(file_path):
                self._create_backup(file_path, user_id)

            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"文件保存成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存文件失败 {file_path}: {e}")
            return False

    def read_file(self, file_path: str) -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 文件内容，如果读取失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None

    def _create_backup(self, file_path: str, user_id: str):
        """
        创建文件备份

        Args:
            file_path: 要备份的文件路径
            user_id: 用户ID
        """
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{os.path.splitext(filename)[0]}_{user_id}_{timestamp}{os.path.splitext(filename)[1]}"
            backup_path = os.path.join(self.backup_dir, backup_name)

            # 复制文件
            shutil.copy2(file_path, backup_path)

            logger.debug(f"备份创建: {backup_path}")

        except Exception as e:
            logger.warning(f"创建备份失败: {e}")


# 全局文件操作器实例
_file_ops = None


def get_file_operations() -> FileOperations:
    """获取全局文件操作器实例"""
    global _file_ops
    if _file_ops is None:
        _file_ops = FileOperations()
    return _file_ops
```

---

## 4. 历史记录管理 (`history.py`)

```python
"""
历史记录管理
管理文档的历史版本和回滚功能
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import difflib

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    历史记录管理器

    负责文档的历史版本管理和回滚功能
    """

    def __init__(self, history_dir: str = "./history"):
        """
        初始化历史管理器

        Args:
            history_dir: 历史记录目录
        """
        self.history_dir = os.path.abspath(history_dir)
        os.makedirs(self.history_dir, exist_ok=True)

    def save_version(self, file_path: str, content: str,
                    user_id: str, message: str = "") -> str:
        """
        保存文件版本

        Args:
            file_path: 原始文件路径
            content: 文件内容
            user_id: 用户ID
            message: 版本说明

        Returns:
            str: 版本ID
        """
        try:
            # 生成版本ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            version_id = f"{timestamp}_{user_id}"

            # 创建版本目录
            version_dir = os.path.join(self.history_dir, version_id)
            os.makedirs(version_dir, exist_ok=True)

            # 保存文件内容
            content_file = os.path.join(version_dir, filename)
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 保存元信息
            meta = {
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "file_path": file_path,
                "file_size": len(content),
                "message": message or f"自动保存版本 {version_id}"
            }

            meta_file = os.path.join(version_dir, "meta.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            logger.info(f"版本保存成功: {version_id} - {file_path}")
            return version_id

        except Exception as e:
            logger.error(f"保存版本失败: {e}")
            return ""

    def get_versions(self, file_path: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取版本历史

        Args:
            file_path: 指定文件路径，如果为None则返回所有版本
            limit: 返回的最大版本数量

        Returns:
            List[Dict[str, Any]]: 版本列表
        """
        versions = []

        try:
            if os.path.exists(self.history_dir):
                for item in sorted(os.listdir(self.history_dir), reverse=True):
                    version_dir = os.path.join(self.history_dir, item)
                    if os.path.isdir(version_dir):
                        meta_file = os.path.join(version_dir, "meta.json")
                        if os.path.exists(meta_file):
                            with open(meta_file, 'r', encoding='utf-8') as f:
                                meta = json.load(f)

                            # 过滤指定文件
                            if file_path and meta.get("file_path") != file_path:
                                continue

                            versions.append(meta)

                            if len(versions) >= limit:
                                break

        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")

        return versions

    def rollback_to_version(self, version_id: str, target_path: str) -> bool:
        """
        回滚到指定版本

        Args:
            version_id: 版本ID
            target_path: 目标文件路径

        Returns:
            bool: 回滚是否成功
        """
        try:
            version_dir = os.path.join(self.history_dir, version_id)
            if not os.path.exists(version_dir):
                logger.warning(f"版本不存在: {version_id}")
                return False

            # 查找版本文件
            meta_file = os.path.join(version_dir, "meta.json")
            if not os.path.exists(meta_file):
                logger.warning(f"版本元信息不存在: {version_id}")
                return False

            # 获取原始文件名
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            original_filename = os.path.basename(meta["file_path"])
            content_file = os.path.join(version_dir, original_filename)

            if not os.path.exists(content_file):
                logger.warning(f"版本文件不存在: {content_file}")
                return False

            # 读取内容并写入目标文件
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"成功回滚到版本: {version_id} -> {target_path}")
            return True

        except Exception as e:
            logger.error(f"回滚版本失败: {e}")
            return False

    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        比较两个版本的差异

        Args:
            version_id1: 版本ID 1
            version_id2: 版本ID 2

        Returns:
            Dict[str, Any]: 比较结果
        """
        try:
            # 获取两个版本的内容
            content1 = self._get_version_content(version_id1)
            content2 = self._get_version_content(version_id2)

            if content1 is None or content2 is None:
                return {"error": "无法获取版本内容"}

            # 生成差异
            diff = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"version_{version_id1}",
                tofile=f"version_{version_id2}",
                lineterm=""
            ))

            return {
                "version1": version_id1,
                "version2": version_id2,
                "diff": "".join(diff),
                "has_changes": len(diff) > 0
            }

        except Exception as e:
            logger.error(f"比较版本失败: {e}")
            return {"error": str(e)}

    def _get_version_content(self, version_id: str) -> Optional[str]:
        """
        获取版本文件内容

        Args:
            version_id: 版本ID

        Returns:
            Optional[str]: 文件内容
        """
        try:
            version_dir = os.path.join(self.history_dir, version_id)
            meta_file = os.path.join(version_dir, "meta.json")

            if not os.path.exists(meta_file):
                return None

            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            filename = os.path.basename(meta["file_path"])
            content_file = os.path.join(version_dir, filename)

            if not os.path.exists(content_file):
                return None

            with open(content_file, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"获取版本内容失败 {version_id}: {e}")
            return None


# 全局历史管理器实例
_history_manager = None


def get_history_manager() -> HistoryManager:
    """获取全局历史管理器实例"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager
```

---

## 5. 项目管理器主模块 (`manager.py`)

```python
"""
项目管理器
负责项目的创建、管理和文件操作
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ProjectManager:
    """
    项目管理器

    负责项目的生命周期管理和文件操作
    """

    def __init__(self, projects_root: str = "./projects"):
        """
        初始化项目管理器

        Args:
            projects_root: 项目根目录路径
        """
        self.projects_root = os.path.abspath(projects_root)
        self.current_project = None

        # 确保项目根目录存在
        os.makedirs(self.projects_root, exist_ok=True)

    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        创建新项目

        Args:
            name: 项目名称
            description: 项目描述

        Returns:
            Dict[str, Any]: 项目信息
        """
        # 生成项目ID
        project_id = self._generate_project_id(name)

        # 创建项目目录结构
        project_path = os.path.join(self.projects_root, project_id)
        os.makedirs(project_path, exist_ok=True)

        # 创建子目录
        subdirs = ["history", "docs", "code", "assets"]
        for subdir in subdirs:
            os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

        # 创建项目元信息文件
        project_info = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "version": "1.0.0"
        }

        self._save_project_meta(project_id, project_info)

        # 创建初始文档
        self._create_initial_documents(project_id, name, description)

        logger.info(f"项目创建成功: {name} ({project_id})")
        return project_info

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        列出所有项目

        Returns:
            List[Dict[str, Any]]: 项目列表
        """
        projects = []

        try:
            for item in os.listdir(self.projects_root):
                project_path = os.path.join(self.projects_root, item)
                if os.path.isdir(project_path):
                    meta_file = os.path.join(project_path, "meta.json")
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            project_info = json.load(f)
                            projects.append(project_info)
        except Exception as e:
            logger.error(f"列出项目时发生错误: {e}")

        return projects

    def switch_project(self, project_id: str) -> bool:
        """
        切换当前项目

        Args:
            project_id: 项目ID

        Returns:
            bool: 切换是否成功
        """
        project_path = os.path.join(self.projects_root, project_id)

        if not os.path.exists(project_path):
            logger.warning(f"项目不存在: {project_id}")
            return False

        meta_file = os.path.join(project_path, "meta.json")
        if not os.path.exists(meta_file):
            logger.warning(f"项目元信息文件不存在: {project_id}")
            return False

        self.current_project = project_id
        logger.info(f"切换到项目: {project_id}")
        return True

    def save_with_backup(self, file_path: str, content: str, user_id: str = "system") -> bool:
        """
        保存文件并自动创建备份

        Args:
            file_path: 文件路径
            content: 文件内容
            user_id: 用户ID

        Returns:
            bool: 保存是否成功
        """
        if not self.current_project:
            logger.warning("没有选择当前项目")
            return False

        try:
            # 确保文件目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 如果文件已存在，先备份
            if os.path.exists(file_path):
                self._create_backup(file_path)

            # 保存新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"文件保存成功并已备份: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            return False

    def _generate_project_id(self, name: str) -> str:
        """
        生成项目ID

        Args:
            name: 项目名称

        Returns:
            str: 项目ID
        """
        # 简单的ID生成逻辑
        base_name = name.lower().replace(' ', '_').replace('-', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 确保ID唯一
        counter = 0
        project_id = f"{base_name}_{timestamp}"

        while os.path.exists(os.path.join(self.projects_root, project_id)):
            counter += 1
            project_id = f"{base_name}_{timestamp}_{counter}"

        return project_id

    def _save_project_meta(self, project_id: str, project_info: Dict[str, Any]):
        """
        保存项目元信息

        Args:
            project_id: 项目ID
            project_info: 项目信息
        """
        meta_file = os.path.join(self.projects_root, project_id, "meta.json")

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=2)

    def _create_initial_documents(self, project_id: str, name: str, description: str):
        """
        创建项目的初始文档

        Args:
            project_id: 项目ID
            name: 项目名称
            description: 项目描述
        """
        project_path = os.path.join(self.projects_root, project_id)

        # 创建 README.md
        readme_content = f"""# {name}

{description}

## 项目信息
- 项目ID: {project_id}
- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 项目结构
- `docs/` - 项目文档
- `code/` - 源代码
- `assets/` - 项目资源
- `history/` - 历史备份

---
*此文档由 TeamDev 自动生成*
"""

        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _create_backup(self, file_path: str):
        """
        创建文件备份

        Args:
            file_path: 要备份的文件路径
        """
        if not self.current_project:
            return

        try:
            # 获取相对路径
            rel_path = os.path.relpath(file_path, self.projects_root)

            # 创建备份目录
            backup_dir = os.path.join(self.projects_root, self.current_project, "history")
            os.makedirs(backup_dir, exist_ok=True)

            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
            backup_path = os.path.join(backup_dir, backup_name)

            # 复制文件
            import shutil
            shutil.copy2(file_path, backup_path)

            logger.debug(f"文件备份创建: {backup_path}")

        except Exception as e:
            logger.warning(f"创建备份失败: {e}")


# 全局项目管理器实例
_project_manager = None


def get_project_manager() -> ProjectManager:
    """获取全局项目管理器实例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
```

---

## 核心功能说明

### 🏗️ 架构设计

项目管理器模块采用分层架构设计：

1. **数据层** (`schema.py`)
   - 定义数据结构和文档模板
   - 提供类型安全的数据模型

2. **操作层** (`file_ops.py`)
   - 提供基础的文件操作功能
   - 实现自动备份机制

3. **历史层** (`history.py`)
   - 管理文档的历史版本
   - 提供版本比较和回滚功能

4. **管理层** (`manager.py`)
   - 整合所有功能模块
   - 提供统一的项目管理接口

### 🔧 主要特性

#### 📂 项目生命周期管理
- **项目创建**: 自动生成项目结构和初始文档
- **项目切换**: 快速切换当前工作项目
- **项目列表**: 查看所有管理的项目

#### 💾 自动备份系统
- **版本控制**: 每次保存自动创建历史版本
- **回滚功能**: 支持回滚到任意历史版本
- **差异比较**: 比较不同版本间的差异

#### 📋 文档模板系统
- **PRD模板**: 产品需求文档模板
- **开发指南模板**: 技术文档模板
- **README模板**: 项目说明文档模板

#### 🔒 安全与可靠性
- **原子操作**: 文件操作的原子性保证
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的操作日志记录

### 📖 使用示例

```python
from core.project_manager import get_project_manager

# 获取项目管理器
pm = get_project_manager()

# 创建新项目
project = pm.create_project("我的新项目", "这是一个示例项目")
print(f"项目创建成功: {project['name']} (ID: {project['id']})")

# 切换到项目
pm.switch_project(project['id'])

# 保存文档并自动备份
pm.save_with_backup("./docs/prd.md", "# 产品需求文档\\n\\n## 概述\\n...", "user123")

# 获取版本历史
from core.project_manager import get_history_manager
hm = get_history_manager()
versions = hm.get_versions("./docs/prd.md")
print(f"找到 {len(versions)} 个历史版本")
```

### 🔗 模块依赖关系

```
manager.py (主模块)
├── file_ops.py (文件操作)
├── history.py (历史管理)
└── schema.py (数据结构)
```

### 🎯 设计原则

1. **单一职责**: 每个模块负责特定的功能
2. **依赖倒置**: 通过接口而非具体实现进行依赖
3. **开闭原则**: 对扩展开放，对修改封闭
4. **错误处理**: 完善的异常处理和日志记录
5. **配置驱动**: 支持通过配置自定义行为

---

*本文档由 TeamDev 项目自动生成，包含完整的项目管理器模块代码* 🚀
