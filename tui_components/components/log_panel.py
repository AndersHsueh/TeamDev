"""
日志输出面板组件
显示日志消息，支持不同级别的日志
"""

import time
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: float
    level: LogLevel
    message: str
    source: str = ""
    data: Any = None
    
    def get_timestamp_str(self) -> str:
        """获取格式化的时间戳"""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))
    
    def get_level_icon(self) -> str:
        """获取级别图标"""
        icons = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨",
        }
        return icons.get(self.level, "ℹ️")


class LogPanelComponent(BaseComponent):
    """日志输出面板组件"""
    
    def __init__(self, name: str = "log_panel"):
        super().__init__(name)
        self.logs: List[LogEntry] = []
        self.max_logs = 1000  # 最大日志条数
        self.scroll_offset = 0
        self.auto_scroll = True
        self.show_timestamp = True
        self.show_level = True
        self.show_source = False
        self.word_wrap = True
        self.filter_levels: List[LogLevel] = list(LogLevel)  # 显示的日志级别
        self.filter_source: Optional[str] = None  # 过滤特定来源
        
        # 级别颜色映射
        self.level_colors = {
            LogLevel.DEBUG: get_color("text_muted"),
            LogLevel.INFO: get_color("text"),
            LogLevel.WARNING: get_color("warning"),
            LogLevel.ERROR: get_color("error"),
            LogLevel.CRITICAL: get_color("error"),
        }
        
        # 回调函数
        self.on_log_added: Optional[Callable[[LogEntry], None]] = None
    
    def add_log(self, level: LogLevel, message: str, source: str = "", data: Any = None) -> None:
        """添加日志条目"""
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            source=source,
            data=data
        )
        
        self.logs.append(entry)
        
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # 自动滚动到底部
        if self.auto_scroll:
            self.scroll_to_bottom()
        
        # 触发回调
        if self.on_log_added:
            self.on_log_added(entry)
    
    def add_debug(self, message: str, source: str = "", data: Any = None) -> None:
        """添加调试日志"""
        self.add_log(LogLevel.DEBUG, message, source, data)
    
    def add_info(self, message: str, source: str = "", data: Any = None) -> None:
        """添加信息日志"""
        self.add_log(LogLevel.INFO, message, source, data)
    
    def add_warning(self, message: str, source: str = "", data: Any = None) -> None:
        """添加警告日志"""
        self.add_log(LogLevel.WARNING, message, source, data)
    
    def add_error(self, message: str, source: str = "", data: Any = None) -> None:
        """添加错误日志"""
        self.add_log(LogLevel.ERROR, message, source, data)
    
    def add_critical(self, message: str, source: str = "", data: Any = None) -> None:
        """添加严重错误日志"""
        self.add_log(LogLevel.CRITICAL, message, source, data)
    
    def clear_logs(self) -> None:
        """清空日志"""
        self.logs.clear()
        self.scroll_offset = 0
    
    def set_max_logs(self, max_logs: int) -> None:
        """设置最大日志条数"""
        self.max_logs = max_logs
        if len(self.logs) > max_logs:
            self.logs = self.logs[-max_logs:]
    
    def set_auto_scroll(self, auto_scroll: bool) -> None:
        """设置自动滚动"""
        self.auto_scroll = auto_scroll
    
    def set_display_options(self, show_timestamp: bool = True, show_level: bool = True, 
                          show_source: bool = False, word_wrap: bool = True) -> None:
        """设置显示选项"""
        self.show_timestamp = show_timestamp
        self.show_level = show_level
        self.show_source = show_source
        self.word_wrap = word_wrap
    
    def set_filter_levels(self, levels: List[LogLevel]) -> None:
        """设置过滤的日志级别"""
        self.filter_levels = levels
    
    def set_filter_source(self, source: Optional[str]) -> None:
        """设置过滤的日志来源"""
        self.filter_source = source
    
    def scroll_to_bottom(self) -> None:
        """滚动到底部"""
        self.scroll_offset = max(0, len(self._get_filtered_logs()) - self.size.height)
    
    def scroll_to_top(self) -> None:
        """滚动到顶部"""
        self.scroll_offset = 0
    
    def _get_filtered_logs(self) -> List[LogEntry]:
        """获取过滤后的日志"""
        filtered = []
        for log in self.logs:
            # 级别过滤
            if log.level not in self.filter_levels:
                continue
            
            # 来源过滤
            if self.filter_source and log.source != self.filter_source:
                continue
            
            filtered.append(log)
        
        return filtered
    
    def _format_log_entry(self, entry: LogEntry, max_width: int) -> List[str]:
        """格式化日志条目"""
        lines = []
        
        # 构建前缀
        prefix_parts = []
        
        if self.show_timestamp:
            prefix_parts.append(entry.get_timestamp_str())
        
        if self.show_level:
            level_icon = entry.get_level_icon()
            level_color = self.level_colors.get(entry.level, get_color("text"))
            prefix_parts.append(f"[{level_color}]{level_icon}[/{level_color}]")
        
        if self.show_source and entry.source:
            prefix_parts.append(f"[{entry.source}]")
        
        prefix = " ".join(prefix_parts)
        
        # 计算消息可用宽度
        message_width = max_width - len(prefix) - 1  # -1 for space
        
        if message_width <= 0:
            message_width = max_width
        
        # 处理消息换行
        message_lines = self._wrap_text(entry.message, message_width)
        
        for i, msg_line in enumerate(message_lines):
            if i == 0:
                line = f"{prefix} {msg_line}"
            else:
                # 后续行只显示缩进
                indent = " " * (len(prefix) + 1)
                line = f"{indent}{msg_line}"
            
            lines.append(line)
        
        return lines
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """文本换行"""
        if not self.word_wrap or width <= 0:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # 单词本身太长，强制截断
                    lines.append(word[:width])
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        filtered_logs = self._get_filtered_logs()
        if not filtered_logs:
            return "\n".join([""] * self.size.height)
        
        lines = []
        current_line = 0
        max_width = self.size.width
        
        # 从滚动偏移开始渲染
        for log in filtered_logs[self.scroll_offset:]:
            if current_line >= self.size.height:
                break
            
            log_lines = self._format_log_entry(log, max_width)
            
            for log_line in log_lines:
                if current_line >= self.size.height:
                    break
                
                # 截断过长的行
                if len(log_line) > max_width:
                    log_line = log_line[:max_width-3] + "..."
                
                lines.append(log_line)
                current_line += 1
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "max_logs" in data:
                self.set_max_logs(data["max_logs"])
            if "auto_scroll" in data:
                self.set_auto_scroll(data["auto_scroll"])
            if "filter_levels" in data:
                self.set_filter_levels(data["filter_levels"])
            if "filter_source" in data:
                self.set_filter_source(data["filter_source"])
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        if not self.visible:
            return False
        
        filtered_logs = self._get_filtered_logs()
        max_scroll = max(0, len(filtered_logs) - self.size.height)
        
        if key == "up" or key == "k":
            # 向上滚动
            if self.scroll_offset > 0:
                self.scroll_offset -= 1
            return True
        
        elif key == "down" or key == "j":
            # 向下滚动
            if self.scroll_offset < max_scroll:
                self.scroll_offset += 1
            return True
        
        elif key == "page_up" or key == "ctrl+u":
            # 向上翻页
            self.scroll_offset = max(0, self.scroll_offset - self.size.height // 2)
            return True
        
        elif key == "page_down" or key == "ctrl+d":
            # 向下翻页
            self.scroll_offset = min(max_scroll, self.scroll_offset + self.size.height // 2)
            return True
        
        elif key == "home" or key == "g":
            # 滚动到顶部
            self.scroll_to_top()
            return True
        
        elif key == "end" or key == "G":
            # 滚动到底部
            self.scroll_to_bottom()
            return True
        
        elif key == "c":
            # 清空日志
            self.clear_logs()
            return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        if not self.visible:
            return False
        
        # 鼠标滚轮处理
        if button == 4:  # 向上滚动
            if self.scroll_offset > 0:
                self.scroll_offset -= 1
            return True
        elif button == 5:  # 向下滚动
            filtered_logs = self._get_filtered_logs()
            max_scroll = max(0, len(filtered_logs) - self.size.height)
            if self.scroll_offset < max_scroll:
                self.scroll_offset += 1
            return True
        
        return False
    
    def get_log_count(self) -> int:
        """获取日志总数"""
        return len(self.logs)
    
    def get_filtered_log_count(self) -> int:
        """获取过滤后的日志数量"""
        return len(self._get_filtered_logs())
    
    def get_logs_by_level(self, level: LogLevel) -> List[LogEntry]:
        """获取指定级别的日志"""
        return [log for log in self.logs if log.level == level]
    
    def export_logs(self, filepath: str) -> bool:
        """导出日志到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for log in self.logs:
                    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log.timestamp))
                    f.write(f"[{timestamp_str}] {log.level.value.upper()}: {log.message}\n")
            return True
        except Exception:
            return False
