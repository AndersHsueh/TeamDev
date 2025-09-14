"""
Agent 状态显示组件
显示 Agent 的头像、状态灯和名称
"""

from typing import Dict, Any, Optional
from enum import Enum
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style
from rich.console import RenderableType


class AgentStatus(Enum):
    """Agent 状态枚举"""
    IDLE = "idle"           # 空闲
    THINKING = "thinking"   # 思考中
    WORKING = "working"     # 工作中
    ERROR = "error"         # 错误
    OFFLINE = "offline"     # 离线


class AgentStatusComponent(BaseComponent):
    """Agent 状态显示组件"""
    
    def __init__(self, *, id: str | None = None, classes: str | None = None, name: str | None = None):
        super().__init__(id=id, classes=classes, name=name)
        self.agent_name = "Agent"
        self.agent_avatar = "🤖"
        self.status = AgentStatus.IDLE
        self.status_message = ""
        self.show_avatar = True
        self.show_status_light = True
        self.show_name = True
        self.show_message = True
        
        # 状态颜色映射
        self.status_colors = {
            AgentStatus.IDLE: get_color("text_secondary"),
            AgentStatus.THINKING: get_color("info"),
            AgentStatus.WORKING: get_color("success"),
            AgentStatus.ERROR: get_color("error"),
            AgentStatus.OFFLINE: get_color("text_muted"),
        }
        
        # 状态图标映射
        self.status_icons = {
            AgentStatus.IDLE: "●",
            AgentStatus.THINKING: "◐",
            AgentStatus.WORKING: "◑",
            AgentStatus.ERROR: "✗",
            AgentStatus.OFFLINE: "○",
        }
    
    def set_agent_info(self, name: str, avatar: str = "🤖") -> None:
        """设置 Agent 信息"""
        self.agent_name = name
        self.agent_avatar = avatar
    
    def set_status(self, status: AgentStatus, message: str = "") -> None:
        """设置 Agent 状态"""
        self.status = status
        self.status_message = message
    
    def set_display_options(self, show_avatar: bool = True, show_status_light: bool = True, 
                          show_name: bool = True, show_message: bool = True) -> None:
        """设置显示选项"""
        self.show_avatar = show_avatar
        self.show_status_light = show_status_light
        self.show_name = show_name
        self.show_message = show_message
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        # AgentStatus组件暂时不需要特殊的更新逻辑
        pass
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        lines = []
        
        # 计算可用宽度
        available_width = self.size.width
        
        # 构建状态行
        status_parts = []
        
        # 头像
        if self.show_avatar:
            status_parts.append(self.agent_avatar)
        
        # 状态灯
        if self.show_status_light:
            status_icon = self.status_icons.get(self.status, "●")
            status_color = self.status_colors.get(self.status, get_color("text"))
            status_parts.append(f"[{status_color}]{status_icon}[/{status_color}]")
        
        # Agent 名称
        if self.show_name:
            status_parts.append(self.agent_name)
        
        # 状态消息
        if self.show_message and self.status_message:
            status_parts.append(f"({self.status_message})")
        
        # 组合状态行
        status_line = " ".join(status_parts)
        
        # 如果内容太长，进行截断
        if len(status_line) > available_width:
            status_line = status_line[:available_width-3] + "..."
        
        lines.append(status_line)
        
        # 添加空行以填充高度
        for _ in range(1, self.size.height):
            lines.append("")
        
        return "\n".join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "name" in data:
                self.agent_name = data["name"]
            if "avatar" in data:
                self.agent_avatar = data["avatar"]
            if "status" in data:
                if isinstance(data["status"], AgentStatus):
                    self.status = data["status"]
                elif isinstance(data["status"], str):
                    try:
                        self.status = AgentStatus(data["status"])
                    except ValueError:
                        pass
            if "message" in data:
                self.status_message = data["message"]
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        # Agent 状态组件通常不处理键盘输入
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        # Agent 状态组件通常不处理鼠标事件
        return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            "name": self.agent_name,
            "avatar": self.agent_avatar,
            "status": self.status.value,
            "message": self.status_message,
            "color": self.status_colors.get(self.status, get_color("text")),
            "icon": self.status_icons.get(self.status, "●"),
        }
