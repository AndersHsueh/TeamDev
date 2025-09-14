"""
项目状态管理模块

负责管理当前工作项目的状态信息
"""

import os
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


@dataclass
class ProjectInfo:
    """
    项目信息数据类
    
    设计为可扩展的项目状态容器
    """
    # 基础信息
    name: str
    path: str
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    # 项目配置
    config: Dict[str, Any] = field(default_factory=dict)
    
    # LLM 相关状态
    llm_configs: Dict[str, Dict] = field(default_factory=dict)
    active_llm: Optional[str] = None
    
    # 工作状态
    current_task: Optional[str] = None
    work_session: Dict[str, Any] = field(default_factory=dict)
    
    # 扩展字段 - 用于未来功能
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 处理 datetime 序列化
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
        """从字典创建实例"""
        # 处理 datetime 反序列化
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_accessed' in data and data['last_accessed']:
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        
        return cls(**data)
    
    def update_access_time(self):
        """更新最后访问时间"""
        self.last_accessed = datetime.now()
    
    def set_extension(self, key: str, value: Any):
        """设置扩展字段"""
        self.extensions[key] = value
    
    def get_extension(self, key: str, default=None):
        """获取扩展字段"""
        return self.extensions.get(key, default)


class ProjectStateManager:
    """
    项目状态管理器 (单例模式)
    
    负责管理当前项目状态的全局对象
    """
    
    _instance = None
    _current_project: Optional[ProjectInfo] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def current_project(self) -> Optional[ProjectInfo]:
        """获取当前项目信息"""
        return self._current_project
    
    @property
    def is_project_selected(self) -> bool:
        """检查是否已选择项目"""
        return self._current_project is not None
    
    def set_current_project(self, project_info: ProjectInfo):
        """设置当前项目"""
        project_info.update_access_time()
        self._current_project = project_info
        
        # 保存到临时状态文件
        self._save_current_state()
    
    def clear_current_project(self):
        """清除当前项目状态"""
        self._current_project = None
        self._clear_current_state()
    
    def switch_project(self, new_project: ProjectInfo):
        """切换项目"""
        if self._current_project:
            # 可以在这里添加切换前的清理逻辑
            pass
        
        self.set_current_project(new_project)
    
    def get_project_config(self, key: str, default=None):
        """获取当前项目配置"""
        if not self._current_project:
            return default
        return self._current_project.config.get(key, default)
    
    def set_project_config(self, key: str, value: Any):
        """设置当前项目配置"""
        if self._current_project:
            self._current_project.config[key] = value
            self._save_current_state()
    
    def _save_current_state(self):
        """保存当前状态到文件"""
        if not self._current_project:
            return
        
        state_dir = Path.home() / '.teamdev'
        state_dir.mkdir(exist_ok=True)
        state_file = state_dir / 'current_project.json'
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self._current_project.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            # 使用日志记录错误，而不是 print
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存项目状态失败: {e}")
    
    def _clear_current_state(self):
        """清除状态文件"""
        state_file = Path.home() / '.teamdev' / 'current_project.json'
        if state_file.exists():
            try:
                state_file.unlink()
            except Exception as e:
                # 使用日志记录错误，而不是 print
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"清除项目状态失败: {e}")
    
    def restore_from_file(self) -> bool:
        """从文件恢复状态"""
        state_file = Path.home() / '.teamdev' / 'current_project.json'
        
        if not state_file.exists():
            return False
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project_info = ProjectInfo.from_dict(data)
            
            # 验证项目路径是否仍然存在
            if Path(project_info.path).exists():
                self._current_project = project_info
                return True
            else:
                # 项目路径不存在，清除状态
                self._clear_current_state()
                return False
                
        except Exception as e:
            # 使用日志记录错误，而不是 print
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"恢复项目状态失败: {e}")
            return False


# 全局项目状态管理器实例
current_project_manager = ProjectStateManager()