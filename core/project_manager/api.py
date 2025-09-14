"""
项目管理API接口
提供项目管理的HTTP API接口
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional
import logging

from .manager import get_project_manager

logger = logging.getLogger(__name__)

# 创建蓝图
project_bp = Blueprint('project', __name__, url_prefix='/api/project')

# 获取项目管理器实例
project_manager = get_project_manager()


@project_bp.route('/create', methods=['POST'])
def create_project():
    """
    创建新项目
    
    请求体:
    {
        "name": "项目名称",
        "description": "项目描述"
    }
    
    返回:
    {
        "success": true,
        "data": {
            "id": "项目ID",
            "name": "项目名称",
            "description": "项目描述",
            "created_at": "创建时间"
        }
    }
    """
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({
                "success": False,
                "error": "项目名称不能为空"
            }), 400
        
        # 创建项目
        project_info = project_manager.create_project(name, description)
        
        return jsonify({
            "success": True,
            "data": project_info
        })
        
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        return jsonify({
            "success": False,
            "error": "创建项目失败"
        }), 500


@project_bp.route('/list', methods=['GET'])
def list_projects():
    """
    列出所有项目
    
    返回:
    {
        "success": true,
        "data": [
            {
                "id": "项目ID",
                "name": "项目名称",
                "description": "项目描述",
                "created_at": "创建时间",
                "status": "项目状态"
            }
        ]
    }
    """
    try:
        projects = project_manager.list_projects()
        
        return jsonify({
            "success": True,
            "data": projects
        })
        
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        return jsonify({
            "success": False,
            "error": "获取项目列表失败"
        }), 500


@project_bp.route('/switch/<project_name>', methods=['POST'])
def switch_project(project_name):
    """
    切换当前项目
    
    参数:
    project_name: 项目名称
    
    返回:
    {
        "success": true,
        "message": "切换成功"
    }
    """
    try:
        success = project_manager.switch_project(project_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"已切换到项目: {project_name}"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"切换项目失败: {project_name}"
            }), 404
            
    except Exception as e:
        logger.error(f"切换项目失败: {e}")
        return jsonify({
            "success": False,
            "error": "切换项目失败"
        }), 500


@project_bp.route('/info/<project_name>', methods=['GET'])
def get_project_info(project_name):
    """
    获取项目信息
    
    参数:
    project_name: 项目名称
    
    返回:
    {
        "success": true,
        "data": {
            "id": "项目ID",
            "name": "项目名称",
            "description": "项目描述",
            "created_at": "创建时间",
            "status": "项目状态"
        }
    }
    """
    try:
        project_info = project_manager.read_project_info(project_name)
        
        if project_info:
            return jsonify({
                "success": True,
                "data": project_info
            })
        else:
            return jsonify({
                "success": False,
                "error": f"项目不存在: {project_name}"
            }), 404
            
    except Exception as e:
        logger.error(f"获取项目信息失败: {e}")
        return jsonify({
            "success": False,
            "error": "获取项目信息失败"
        }), 500


@project_bp.route('/update/<project_name>', methods=['POST'])
def update_project(project_name):
    """
    更新项目信息
    
    参数:
    project_name: 项目名称
    
    请求体:
    {
        "description": "新的项目描述",
        "status": "新的项目状态"
    }
    
    返回:
    {
        "success": true,
        "message": "更新成功"
    }
    """
    try:
        data = request.get_json()
        
        # 更新项目信息
        success = project_manager.update_project_info(project_name, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "项目信息更新成功"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"更新项目信息失败: {project_name}"
            }), 404
            
    except Exception as e:
        logger.error(f"更新项目信息失败: {e}")
        return jsonify({
            "success": False,
            "error": "更新项目信息失败"
        }), 500


def write_agent_doc(project_name: str, agent_name: str, content: str) -> bool:
    """
    为Agent写入文档
    
    Args:
        project_name (str): 项目名称
        agent_name (str): Agent名称 (monica, jacky, happen, fei, peipei)
        content (str): 文档内容
    
    Returns:
        bool: 是否写入成功
    """
    try:
        # 构建文档路径
        doc_path = f"./user-documents/{project_name}/docs/{agent_name}/index.md"
        
        # 保存文档
        success = project_manager.save_with_backup(doc_path, content)
        
        if success:
            logger.info(f"Agent文档写入成功: {agent_name}")
        else:
            logger.error(f"Agent文档写入失败: {agent_name}")
            
        return success
        
    except Exception as e:
        logger.error(f"写入Agent文档时发生错误: {e}")
        return False


def read_agent_doc(project_name: str, agent_name: str) -> Optional[str]:
    """
    读取Agent文档
    
    Args:
        project_name (str): 项目名称
        agent_name (str): Agent名称 (monica, jacky, happen, fei, peipei)
    
    Returns:
        Optional[str]: 文档内容，如果不存在返回None
    """
    try:
        # 构建文档路径
        doc_path = f"./user-documents/{project_name}/docs/{agent_name}/index.md"
        
        # 读取文档
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return content
        
    except FileNotFoundError:
        logger.warning(f"Agent文档不存在: {agent_name}")
        return None
    except Exception as e:
        logger.error(f"读取Agent文档时发生错误: {e}")
        return None
