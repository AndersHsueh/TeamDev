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
    README_TEMPLATE,
    PROJECT_INFO_TEMPLATE
)
from .history import HistoryManager, get_history_manager
from .api import (
    create_project,
    read_project_info,
    update_project_info,
    switch_project,
    write_agent_doc,
    save_code_file,
    list_projects,
    get_project_progress,
    validate_project_structure,
    get_current_project,
    set_project_root
)

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
    "README_TEMPLATE",
    "PROJECT_INFO_TEMPLATE",

    # API接口
    "create_project",
    "read_project_info",
    "update_project_info",
    "switch_project",
    "write_agent_doc",
    "save_code_file",
    "list_projects",
    "get_project_progress",
    "validate_project_structure",
    "get_current_project",
    "set_project_root"
]
