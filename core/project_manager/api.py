"""
项目管理API接口
提供给Agent使用的标准化接口
"""

import logging
from typing import Dict, Any, Optional, List

from .manager import ProjectManager, get_project_manager

logger = logging.getLogger(__name__)


# P0 - 必须实现的基础接口
def create_project(name: str, description: str = "") -> Dict[str, Any]:
    """
    创建新项目

    Args:
        name: 项目名称
        description: 项目描述

    Returns:
        Dict[str, Any]: 项目信息
    """
    try:
        pm = get_project_manager()
        result = pm.create_project(name, description)
        logger.info(f"API: 项目创建成功 - {name}")
        return {
            "success": True,
            "data": result,
            "message": f"项目 '{name}' 创建成功"
        }
    except Exception as e:
        logger.error(f"API: 项目创建失败 - {name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{name}' 创建失败"
        }


def read_project_info(project_name: str) -> Dict[str, Any]:
    """
    读取项目信息

    Args:
        project_name: 项目名称

    Returns:
        Dict[str, Any]: 项目信息
    """
    try:
        pm = get_project_manager()
        result = pm.read_project_info(project_name)
        if result:
            return {
                "success": True,
                "data": result,
                "message": f"项目 '{project_name}' 信息读取成功"
            }
        else:
            return {
                "success": False,
                "error": "项目不存在",
                "message": f"项目 '{project_name}' 不存在"
            }
    except Exception as e:
        logger.error(f"API: 项目信息读取失败 - {project_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{project_name}' 信息读取失败"
        }


def update_project_info(project_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新项目信息

    Args:
        project_name: 项目名称
        updates: 要更新的字段

    Returns:
        Dict[str, Any]: 更新结果
    """
    try:
        pm = get_project_manager()
        success = pm.update_project_info(project_name, updates)
        if success:
            return {
                "success": True,
                "message": f"项目 '{project_name}' 信息更新成功"
            }
        else:
            return {
                "success": False,
                "error": "更新失败",
                "message": f"项目 '{project_name}' 信息更新失败"
            }
    except Exception as e:
        logger.error(f"API: 项目信息更新失败 - {project_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{project_name}' 信息更新失败"
        }


def switch_project(project_name: str) -> Dict[str, Any]:
    """
    切换当前项目上下文

    Args:
        project_name: 项目名称

    Returns:
        Dict[str, Any]: 切换结果
    """
    try:
        pm = get_project_manager()
        success = pm.switch_project(project_name)
        if success:
            return {
                "success": True,
                "message": f"已切换到项目 '{project_name}'"
            }
        else:
            return {
                "success": False,
                "error": "项目不存在",
                "message": f"项目 '{project_name}' 不存在或无法切换"
            }
    except Exception as e:
        logger.error(f"API: 项目切换失败 - {project_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{project_name}' 切换失败"
        }


# P1 - Agent协作支持接口
def write_agent_doc(project_name: str, agent_name: str, filename: str, content: str) -> Dict[str, Any]:
    """
    为Agent写入文档

    Args:
        project_name: 项目名称
        agent_name: Agent名称 (jim, jacky, happen, fei, peipei)
        filename: 文件名
        content: 文档内容

    Returns:
        Dict[str, Any]: 写入结果
    """
    try:
        pm = get_project_manager()

        # 切换到指定项目
        switch_result = pm.switch_project(project_name)
        if not switch_result:
            return {
                "success": False,
                "error": "项目不存在",
                "message": f"项目 '{project_name}' 不存在"
            }

        # 构建文档路径
        doc_path = f"./user-documents/{project_name}/docs/{agent_name}/{filename}"

        # 保存文档
        success = pm.save_with_backup(doc_path, content, agent_name)

        if success:
            return {
                "success": True,
                "message": f"Agent文档保存成功: {doc_path}",
                "path": doc_path
            }
        else:
            return {
                "success": False,
                "error": "保存失败",
                "message": f"Agent文档保存失败: {doc_path}"
            }
    except Exception as e:
        logger.error(f"API: Agent文档写入失败 - {project_name}/{agent_name}/{filename}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Agent文档写入失败: {filename}"
        }


def save_code_file(project_name: str, filepath: str, content: str) -> Dict[str, Any]:
    """
    保存代码文件

    Args:
        project_name: 项目名称
        filepath: 相对路径 (相对于src目录)
        content: 代码内容

    Returns:
        Dict[str, Any]: 保存结果
    """
    try:
        pm = get_project_manager()

        # 切换到指定项目
        switch_result = pm.switch_project(project_name)
        if not switch_result:
            return {
                "success": False,
                "error": "项目不存在",
                "message": f"项目 '{project_name}' 不存在"
            }

        # 构建代码文件路径
        code_path = f"./user-documents/{project_name}/src/{filepath}"

        # 保存代码文件
        success = pm.save_with_backup(code_path, content, "happen")

        if success:
            return {
                "success": True,
                "message": f"代码文件保存成功: {code_path}",
                "path": code_path
            }
        else:
            return {
                "success": False,
                "error": "保存失败",
                "message": f"代码文件保存失败: {code_path}"
            }
    except Exception as e:
        logger.error(f"API: 代码文件保存失败 - {project_name}/{filepath}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"代码文件保存失败: {filepath}"
        }


# P2 - 增强功能接口
def list_projects() -> Dict[str, Any]:
    """
    列出所有项目及其状态

    Returns:
        Dict[str, Any]: 项目列表
    """
    try:
        pm = get_project_manager()
        projects = pm.list_projects()

        return {
            "success": True,
            "data": projects,
            "count": len(projects),
            "message": f"找到 {len(projects)} 个项目"
        }
    except Exception as e:
        logger.error(f"API: 项目列表获取失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "项目列表获取失败"
        }


def get_project_progress(project_name: str) -> Dict[str, Any]:
    """
    获取项目进度统计

    Args:
        project_name: 项目名称

    Returns:
        Dict[str, Any]: 项目进度信息
    """
    try:
        # 读取项目信息
        project_info = read_project_info(project_name)
        if not project_info["success"]:
            return project_info

        # 这里可以根据实际的Todo状态进行统计
        # 目前返回基础信息
        progress = {
            "project_name": project_name,
            "status": project_info["data"]["status"],
            "total_tasks": 12,  # 从模板中的任务数
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "pending_tasks": 12,
            "completion_rate": 0.0
        }

        return {
            "success": True,
            "data": progress,
            "message": f"项目 '{project_name}' 进度获取成功"
        }
    except Exception as e:
        logger.error(f"API: 项目进度获取失败 - {project_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{project_name}' 进度获取失败"
        }


def validate_project_structure(project_name: str) -> Dict[str, Any]:
    """
    验证项目目录结构完整性

    Args:
        project_name: 项目名称

    Returns:
        Dict[str, Any]: 验证结果
    """
    try:
        import os
        pm = get_project_manager()

        project_path = f"./user-documents/{project_name}"
        if not os.path.exists(project_path):
            return {
                "success": False,
                "error": "项目目录不存在",
                "message": f"项目 '{project_name}' 目录不存在"
            }

        # 检查必需的文件和目录
        required_items = [
            "project-info.md",
            "docs",
            "src",
            "assets",
            "docs/jim",
            "docs/jacky",
            "docs/happen",
            "docs/fei",
            "docs/peipei"
        ]

        missing_items = []
        for item in required_items:
            item_path = os.path.join(project_path, item)
            if not os.path.exists(item_path):
                missing_items.append(item)

        if missing_items:
            return {
                "success": False,
                "error": "目录结构不完整",
                "missing_items": missing_items,
                "message": f"项目 '{project_name}' 缺少以下项目: {', '.join(missing_items)}"
            }

        return {
            "success": True,
            "message": f"项目 '{project_name}' 目录结构验证通过"
        }
    except Exception as e:
        logger.error(f"API: 项目结构验证失败 - {project_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"项目 '{project_name}' 结构验证失败"
        }


# 工具函数
def get_current_project() -> Optional[str]:
    """
    获取当前项目名称

    Returns:
        Optional[str]: 当前项目名称，如果没有设置则返回None
    """
    pm = get_project_manager()
    return pm.current_project


def set_project_root(root_path: str):
    """
    设置项目根目录

    Args:
        root_path: 新的根目录路径
    """
    pm = get_project_manager()
    pm.projects_root = root_path
    pm._ensure_project_root_exists()
