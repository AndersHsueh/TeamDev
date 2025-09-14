"""
项目选择器模块

负责项目选择和创建的用户交互
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from .project_state import ProjectInfo, current_project_manager

logger = logging.getLogger(__name__)


class ProjectSelector:
    """项目选择器"""
    
    def __init__(self, user_documents_path: str = "./user-documents"):
        self.user_documents_path = Path(user_documents_path)
        self.user_documents_path.mkdir(exist_ok=True)
    
    def get_available_projects(self) -> List[ProjectInfo]:
        """获取可用项目列表"""
        projects = []
        
        if not self.user_documents_path.exists():
            return projects
        
        for item in self.user_documents_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 检查是否有项目配置文件
                config_file = item / '.teamdev.json'
                
                if config_file.exists():
                    # 从配置文件读取项目信息
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        
                        project_info = ProjectInfo(
                            name=config_data.get('name', item.name),
                            path=str(item),
                            created_at=datetime.fromisoformat(config_data['created_at']) if 'created_at' in config_data else None,
                            config=config_data.get('config', {})
                        )
                        projects.append(project_info)
                        logger.debug(f"加载项目配置: {project_info.name}")
                    except Exception as e:
                        # 配置文件损坏，创建基础项目信息
                        logger.warning(f"项目配置文件损坏 {config_file}: {e}")
                        project_info = ProjectInfo(
                            name=item.name,
                            path=str(item),
                            created_at=datetime.fromtimestamp(item.stat().st_ctime)
                        )
                        projects.append(project_info)
                else:
                    # 没有配置文件，创建基础项目信息
                    project_info = ProjectInfo(
                        name=item.name,
                        path=str(item),
                        created_at=datetime.fromtimestamp(item.stat().st_ctime)
                    )
                    projects.append(project_info)
        
        # 按最后访问时间排序
        projects.sort(key=lambda p: p.last_accessed or p.created_at or datetime.min, reverse=True)
        logger.info(f"发现 {len(projects)} 个项目")
        return projects
    
    def create_new_project(self, name: str) -> ProjectInfo:
        """创建新项目"""
        project_path = self.user_documents_path / name
        
        if project_path.exists():
            raise ValueError(f"项目 '{name}' 已存在")
        
        # 创建项目目录
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建项目信息
        project_info = ProjectInfo(
            name=name,
            path=str(project_path),
            created_at=datetime.now()
        )
        
        # 保存项目配置
        self._save_project_config(project_info)
        
        logger.info(f"创建新项目: {name} at {project_path}")
        return project_info
    
    def _save_project_config(self, project_info: ProjectInfo):
        """保存项目配置到项目目录"""
        config_file = Path(project_info.path) / '.teamdev.json'
        
        try:
            config_data = {
                'name': project_info.name,
                'created_at': project_info.created_at.isoformat() if project_info.created_at else None,
                'config': project_info.config
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"保存项目配置: {config_file}")
        except Exception as e:
            logger.error(f"保存项目配置失败: {e}")
    
    def show_project_selection_dialog(self) -> Optional[ProjectInfo]:
        """显示项目选择对话框"""
        projects = self.get_available_projects()
        
        print("\n=== TeamDev 项目选择 ===")
        print("请选择要处理的项目:")
        
        if projects:
            for i, project in enumerate(projects, 1):
                last_accessed = project.last_accessed.strftime("%Y-%m-%d %H:%M") if project.last_accessed else "从未访问"
                print(f"{i}. {project.name} (最后访问: {last_accessed})")
        else:
            print("当前没有可用项目")
        
        print(f"{len(projects) + 1}. 创建新项目")
        print("0. 退出")
        
        while True:
            try:
                choice = input(f"\n请输入选项 (0-{len(projects) + 1}): ").strip()
                
                if choice == "0":
                    logger.info("用户选择退出")
                    return None
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(projects):
                    # 选择现有项目
                    selected_project = projects[choice_num - 1]
                    logger.info(f"用户选择项目: {selected_project.name}")
                    return selected_project
                
                elif choice_num == len(projects) + 1:
                    # 创建新项目
                    return self._create_new_project_interactive()
                
                else:
                    print("无效选项，请重新输入")
                    
            except ValueError:
                print("无效输入，请输入数字")
            except KeyboardInterrupt:
                print("\n用户取消操作")
                logger.info("用户键盘中断操作")
                return None
    
    def _create_new_project_interactive(self) -> Optional[ProjectInfo]:
        """交互式创建新项目"""
        while True:
            try:
                name = input("请输入项目名称: ").strip()
                
                if not name:
                    print("项目名称不能为空")
                    continue
                
                if any(char in name for char in r'<>:"/\|?*'):
                    print("项目名称包含无效字符")
                    continue
                
                return self.create_new_project(name)
                
            except ValueError as e:
                print(f"错误: {e}")
                logger.error(f"创建项目失败: {e}")
            except KeyboardInterrupt:
                print("\n用户取消操作")
                logger.info("用户取消创建新项目")
                return None