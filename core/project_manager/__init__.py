"""
项目管理模块
提供项目生命周期管理和文件操作功能，以及项目状态管理
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
# 暂时注释掉 api 导入，避免 flask 依赖问题
# from .api import (
#     create_project,
#     switch_project,
#     list_projects
# )
from .project_state import ProjectInfo, ProjectStateManager, current_project_manager
from .project_selector import ProjectSelector


# 导出项目系统初始化和切换功能
def initialize_project_system() -> bool:
    """
    初始化项目系统
    
    在系统启动时调用，处理项目选择逻辑
    
    Returns:
        bool: True 如果成功选择项目，False 如果用户取消
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 尝试从文件恢复状态
    if current_project_manager.restore_from_file():
        project = current_project_manager.current_project
        if project:  # 添加空值检查
            print(f"恢复上次工作项目: {project.name}")
            logger.info(f"恢复上次工作项目: {project.name}")
            
            # 询问是否继续使用
            choice = input(f"是否继续使用项目 '{project.name}'? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '']:
                logger.info(f"继续使用项目: {project.name}")
                return True
            else:
                current_project_manager.clear_current_project()
                logger.info("用户选择不继续使用上次项目")
    
    # 显示项目选择对话框
    selector = ProjectSelector()
    selected_project = selector.show_project_selection_dialog()
    
    if selected_project:
        current_project_manager.set_current_project(selected_project)
        print(f"已选择项目: {selected_project.name}")
        logger.info(f"已选择项目: {selected_project.name}")
        return True
    else:
        print("未选择项目，退出系统")
        logger.info("未选择项目，退出系统")
        return False


def switch_project_interactive() -> bool:
    """
    切换项目 (/switch 命令使用)
    
    Returns:
        bool: True 如果成功切换项目
    """
    import logging
    logger = logging.getLogger(__name__)
    
    selector = ProjectSelector()
    new_project = selector.show_project_selection_dialog()
    
    if new_project:
        current_project_manager.switch_project(new_project)
        print(f"已切换到项目: {new_project.name}")
        logger.info(f"已切换到项目: {new_project.name}")
        return True
    else:
        print("取消切换项目")
        logger.info("用户取消切换项目")
        return False

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

    # API接口 (暂时注释掉)
    # "create_project",
    # "switch_project", 
    # "list_projects",

    # 项目状态管理
    "ProjectInfo",
    "ProjectStateManager",
    "current_project_manager",
    "ProjectSelector",
    "initialize_project_system",
    "switch_project_interactive"
]
