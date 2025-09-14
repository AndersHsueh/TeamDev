#!/usr/bin/env python3
"""
项目管理命令模块 (Project Management Command Module)

功能说明:
- 实现/project命令，用于项目管理相关操作
- 提供项目选择、创建、查看等功能
- 与项目状态管理系统集成

核心功能:
1. 显示当前项目信息
2. 选择/切换项目
3. 创建新项目
4. 列出所有可用项目

作用:
提供完整的项目管理命令接口
"""

import logging
from commands.command_base import CommandBase
from core.project_manager import (
    current_project_manager, 
    switch_project_interactive, 
    ProjectSelector
)

logger = logging.getLogger(__name__)


class ProjectCommand(CommandBase):
    def __init__(self):
        super().__init__("project", "项目管理", need_confirm=False)

    def execute(self, args: str) -> str:
        """
        执行项目管理命令
        
        Args:
            args: 命令参数
                - 无参数: 显示当前项目信息
                - "list": 列出所有项目
                - "select": 选择项目
                - "create <name>": 创建新项目
                
        Returns:
            str: 执行结果信息
        """
        try:
            args = args.strip()
            
            if not args:
                # 显示当前项目信息
                return self._show_current_project()
            
            elif args == "list":
                # 列出所有项目
                return self._list_projects()
            
            elif args == "select":
                # 选择项目
                return self._select_project()
            
            elif args.startswith("create "):
                # 创建新项目
                project_name = args[7:].strip()
                return self._create_project(project_name)
            
            else:
                return self._show_help()
                
        except Exception as e:
            error_msg = f"❌ 项目命令执行失败: {str(e)}"
            logger.error(f"项目命令执行失败: {e}")
            return error_msg

    def _show_current_project(self) -> str:
        """显示当前项目信息"""
        current_project = current_project_manager.current_project
        
        if current_project:
            result = f"📁 当前项目信息:\n"
            result += f"  名称: {current_project.name}\n"
            result += f"  路径: {current_project.path}\n"
            
            if current_project.created_at:
                result += f"  创建时间: {current_project.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if current_project.last_accessed:
                result += f"  最后访问: {current_project.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if current_project.config:
                result += f"  配置项数量: {len(current_project.config)}\n"
                
            return result
        else:
            return "⚠️ 当前没有选择项目\n使用 '/project select' 选择项目"

    def _list_projects(self) -> str:
        """列出所有项目"""
        try:
            selector = ProjectSelector()
            projects = selector.get_available_projects()
            
            if not projects:
                return "📂 没有找到可用项目\n使用 '/project create <名称>' 创建新项目"
            
            result = f"📂 可用项目列表 (共 {len(projects)} 个):\n\n"
            
            current_project = current_project_manager.current_project
            current_path = current_project.path if current_project else None
            
            for i, project in enumerate(projects, 1):
                marker = "👉 " if project.path == current_path else "   "
                last_access = project.last_accessed.strftime('%m-%d %H:%M') if project.last_accessed else "从未访问"
                result += f"{marker}{i}. {project.name}\n"
                result += f"     路径: {project.path}\n"
                result += f"     最后访问: {last_access}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"列出项目失败: {e}")
            return f"❌ 列出项目失败: {str(e)}"

    def _select_project(self) -> str:
        """选择项目"""
        try:
            if switch_project_interactive():
                new_project = current_project_manager.current_project
                if new_project:
                    result = f"✅ 已选择项目: {new_project.name}\n"
                    result += f"项目路径: {new_project.path}"
                    logger.info(f"通过命令选择项目: {new_project.name}")
                    return result
                else:
                    return "⚠️ 项目选择后状态异常"
            else:
                return "❌ 项目选择已取消"
                
        except Exception as e:
            logger.error(f"选择项目失败: {e}")
            return f"❌ 选择项目失败: {str(e)}"

    def _create_project(self, project_name: str) -> str:
        """创建新项目"""
        if not project_name:
            return "❌ 请提供项目名称\n使用: /project create <项目名称>"
        
        try:
            selector = ProjectSelector()
            project_info = selector.create_new_project(project_name)
            
            # 自动切换到新创建的项目
            current_project_manager.set_current_project(project_info)
            
            result = f"✅ 项目创建成功: {project_name}\n"
            result += f"项目路径: {project_info.path}\n"
            result += f"已自动切换到新项目"
            
            logger.info(f"创建新项目: {project_name}")
            return result
            
        except ValueError as e:
            return f"❌ 创建项目失败: {str(e)}"
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            return f"❌ 创建项目失败: {str(e)}"

    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
项目管理命令帮助:

/project              - 显示当前项目信息
/project list         - 列出所有可用项目
/project select       - 选择/切换项目
/project create <名称> - 创建新项目

示例:
  /project                    # 查看当前项目
  /project list               # 列出所有项目
  /project select             # 选择项目
  /project create 我的新项目    # 创建项目

别名:
  /p - 简写形式
"""

    def get_help(self) -> str:
        """获取命令帮助信息"""
        return self._show_help()


# 简写别名
class PCommand(ProjectCommand):
    """项目命令的简写形式"""
    def __init__(self):
        super().__init__()
        self.name = "p"