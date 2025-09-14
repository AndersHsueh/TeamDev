#!/usr/bin/env python3
"""
状态栏组件模块 (Status Panel Component Module)

功能说明:
- 显示在界面底部的状态栏，位于输入框下方
- 用于显示系统状态、提示信息、快捷键说明等
- 支持不同类型的状态信息（普通、警告、错误等）
- 可以动态更新状态信息内容和样式

核心功能:
1. 显示当前系统状态信息
2. 显示用户操作提示和快捷键
3. 支持不同状态类型的样式显示
4. 支持临时消息显示和自动清除

作用:
为用户提供实时的系统状态反馈和操作指导，
提升用户体验和操作效率。
"""

import time
from typing import Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
from ..core.base_component import BaseComponent


class StatusType(Enum):
    """状态类型"""
    NORMAL = "normal"      # 普通状态信息
    SUCCESS = "success"    # 成功状态
    WARNING = "warning"    # 警告状态
    ERROR = "error"        # 错误状态
    INFO = "info"          # 提示信息
    HELP = "help"          # 帮助信息


@dataclass
class StatusMessage:
    """状态消息"""
    text: str
    status_type: StatusType = StatusType.NORMAL
    timestamp: Optional[float] = None
    auto_clear: bool = False
    duration: float = 5.0  # 自动清除时间（秒）
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        if not self.auto_clear or self.timestamp is None:
            return False
        return time.time() - self.timestamp > self.duration
    
    def get_icon(self) -> str:
        """获取状态图标"""
        icons = {
            StatusType.NORMAL: "",
            StatusType.SUCCESS: "✅",
            StatusType.WARNING: "⚠️",
            StatusType.ERROR: "❌",
            StatusType.INFO: "ℹ️",
            StatusType.HELP: "💡",
        }
        return icons.get(self.status_type, "")


class StatusPanelComponent(BaseComponent):
    """状态栏组件"""
    
    def __init__(
        self,
        *,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        name: Optional[str] = None,
        default_message: str = "就绪",
    ):
        super().__init__(id=id, classes=classes, name=name)
        self.default_message = default_message
        self.current_message: Optional[StatusMessage] = None
        self.permanent_info: Dict[str, str] = {}
        
        # 设置默认状态
        self.set_status(default_message, StatusType.NORMAL)
    
    def render(self) -> str:
        """渲染状态栏"""
        # 检查当前消息是否过期
        if self.current_message and self.current_message.is_expired():
            self.clear_status()
        
        # 构建显示内容
        parts = []
        
        # 添加当前状态消息
        if self.current_message:
            icon = self.current_message.get_icon()
            text = self.current_message.text
            if icon:
                parts.append(f"{icon} {text}")
            else:
                parts.append(text)
        
        # 添加永久信息（如快捷键提示）
        if self.permanent_info:
            for key, value in self.permanent_info.items():
                parts.append(f"{key}: {value}")
        
        # 如果没有内容，显示默认消息
        if not parts:
            parts.append(self.default_message)
        
        # 用分隔符连接所有部分
        content = " | ".join(parts)
        
        # 确保内容不超过可用宽度
        try:
            width = self.size.width if hasattr(self, 'size') and self.size.width > 0 else 80
        except:
            width = 80
            
        if len(content) > width - 2:  # 留出边距
            content = content[:width-5] + "..."
        
        return content
    
    def update(self, data: Any = None) -> None:
        """更新状态栏（检查过期消息）"""
        if self.current_message and self.current_message.is_expired():
            self.clear_status()
            self.refresh()
    
    def set_status(
        self, 
        message: str, 
        status_type: StatusType = StatusType.NORMAL,
        auto_clear: bool = False,
        duration: float = 5.0
    ) -> None:
        """设置状态消息"""
        self.current_message = StatusMessage(
            text=message,
            status_type=status_type,
            auto_clear=auto_clear,
            duration=duration
        )
        self.refresh()
    
    def set_success(self, message: str, auto_clear: bool = True) -> None:
        """设置成功状态"""
        self.set_status(message, StatusType.SUCCESS, auto_clear)
    
    def set_warning(self, message: str, auto_clear: bool = True) -> None:
        """设置警告状态"""
        self.set_status(message, StatusType.WARNING, auto_clear)
    
    def set_error(self, message: str, auto_clear: bool = True) -> None:
        """设置错误状态"""
        self.set_status(message, StatusType.ERROR, auto_clear)
    
    def set_info(self, message: str, auto_clear: bool = False) -> None:
        """设置信息状态"""
        self.set_status(message, StatusType.INFO, auto_clear)
    
    def set_help(self, message: str, auto_clear: bool = False) -> None:
        """设置帮助信息"""
        self.set_status(message, StatusType.HELP, auto_clear)
    
    def clear_status(self) -> None:
        """清除当前状态，返回默认状态"""
        self.current_message = StatusMessage(
            text=self.default_message,
            status_type=StatusType.NORMAL
        )
        self.refresh()
    
    def add_permanent_info(self, key: str, value: str) -> None:
        """添加永久显示的信息（如快捷键）"""
        self.permanent_info[key] = value
        self.refresh()
    
    def remove_permanent_info(self, key: str) -> None:
        """移除永久信息"""
        if key in self.permanent_info:
            del self.permanent_info[key]
            self.refresh()
    
    def clear_permanent_info(self) -> None:
        """清除所有永久信息"""
        self.permanent_info.clear()
        self.refresh()
    
    def show_ready(self) -> None:
        """显示就绪状态"""
        self.set_status("就绪", StatusType.SUCCESS)
    
    def show_busy(self, task: str = "处理中") -> None:
        """显示忙碌状态"""
        self.set_status(f"🔄 {task}...", StatusType.INFO)
    
    def show_shortcuts(self) -> None:
        """显示常用快捷键"""
        self.clear_permanent_info()
        self.add_permanent_info("Ctrl+Q", "退出")
        self.add_permanent_info("Ctrl+T", "切换主题")
        self.add_permanent_info("/help", "帮助")