"""
项目管理器
负责项目的创建、管理和文件操作
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

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

    def __init__(self, projects_root: str = "./user-documents"):
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
        project_path = os.path.join(self.projects_root, name)  # 使用项目名称作为目录名
        os.makedirs(project_path, exist_ok=True)

        # 创建子目录
        subdirs = ["docs", "src", "assets"]
        for subdir in subdirs:
            os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

        # 创建Agent特定的文档目录
        agent_dirs = ["docs/jim", "docs/jacky", "docs/happen", "docs/fei", "docs/peipei"]
        for agent_dir in agent_dirs:
            os.makedirs(os.path.join(project_path, agent_dir), exist_ok=True)

        # 创建项目基本信息
        project_info = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "version": "1.0.0"
        }

        # 创建 project-info.md 文件
        self._create_project_info_file(name, project_info)

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
                    # 检查是否存在 project-info.md
                    info_file = os.path.join(project_path, "project-info.md")
                    if os.path.exists(info_file):
                        # 从 project-info.md 解析项目信息
                        project_info = self._parse_project_info_file(item, info_file)
                        if project_info:
                            projects.append(project_info)
        except Exception as e:
            logger.error(f"列出项目时发生错误: {e}")

        return projects

    def switch_project(self, project_name: str) -> bool:
        """
        切换当前项目

        Args:
            project_name: 项目名称

        Returns:
            bool: 切换是否成功
        """
        project_path = os.path.join(self.projects_root, project_name)

        if not os.path.exists(project_path):
            logger.warning(f"项目不存在: {project_name}")
            return False

        info_file = os.path.join(project_path, "project-info.md")
        if not os.path.exists(info_file):
            logger.warning(f"项目信息文件不存在: {project_name}")
            return False

        self.current_project = project_name
        logger.info(f"切换到项目: {project_name}")
        return True

    def read_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        读取项目信息

        Args:
            project_name: 项目名称

        Returns:
            Optional[Dict[str, Any]]: 项目信息，如果不存在返回None
        """
        project_path = os.path.join(self.projects_root, project_name)
        info_file = os.path.join(project_path, "project-info.md")

        if not os.path.exists(info_file):
            return None

        return self._parse_project_info_file(project_name, info_file)

    def update_project_info(self, project_name: str, updates: Dict[str, Any]) -> bool:
        """
        更新项目信息

        Args:
            project_name: 项目名称
            updates: 要更新的字段

        Returns:
            bool: 更新是否成功
        """
        try:
            # 读取当前信息
            current_info = self.read_project_info(project_name)
            if not current_info:
                logger.warning(f"项目不存在或信息文件损坏: {project_name}")
                return False

            # 更新字段
            current_info.update(updates)
            current_info["updated_at"] = datetime.now().isoformat()

            # 重新生成 project-info.md
            self._create_project_info_file(project_name, current_info)

            logger.info(f"项目信息更新成功: {project_name}")
            return True

        except Exception as e:
            logger.error(f"更新项目信息失败: {e}")
            return False

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
        import uuid
        return str(uuid.uuid4())[:8]

    def _create_project_info_file(self, project_name: str, project_info: Dict[str, Any]):
        """
        创建 project-info.md 文件

        Args:
            project_name: 项目名称
            project_info: 项目信息
        """
        from .schema import PROJECT_INFO_TEMPLATE

        # 格式化时间
        created_at = datetime.fromisoformat(project_info["created_at"]).strftime('%Y-%m-%d %H:%M:%S')

        content = PROJECT_INFO_TEMPLATE.format(
            project_name=project_info["name"],
            project_id=project_info["id"],
            description=project_info.get("description", "暂无描述"),
            created_at=created_at,
            status=project_info.get("status", "active"),
            version=project_info.get("version", "1.0.0")
        )

        project_path = os.path.join(self.projects_root, project_name)
        info_file = os.path.join(project_path, "project-info.md")

        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _parse_project_info_file(self, project_name: str, info_file_path: str) -> Optional[Dict[str, Any]]:
        """
        解析 project-info.md 文件

        Args:
            project_name: 项目名称
            info_file_path: 文件路径

        Returns:
            Optional[Dict[str, Any]]: 解析后的项目信息
        """
        try:
            with open(info_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析基本信息
            project_info = {
                "name": project_name,
                "description": "",
                "status": "active",
                "version": "1.0.0",
                "created_at": "",
                "updated_at": datetime.now().isoformat()
            }

            lines = content.split('\n')
            in_basic_info = False

            for line in lines:
                line = line.strip()
                if line.startswith('- **项目ID**:'):
                    project_info["id"] = line.split('`')[1]
                elif line.startswith('- **项目名称**:'):
                    project_info["name"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **项目描述**:'):
                    project_info["description"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **创建时间**:'):
                    project_info["created_at"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **项目状态**:'):
                    project_info["status"] = line.split(':', 1)[1].strip()
                elif line.startswith('- **项目版本**:'):
                    project_info["version"] = line.split(':', 1)[1].strip()

            return project_info

        except Exception as e:
            logger.error(f"解析项目信息文件失败 {info_file_path}: {e}")
            return None

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
