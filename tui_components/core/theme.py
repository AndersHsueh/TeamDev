"""
主题和样式定义
定义颜色、样式和主题相关的常量
"""

from typing import Dict, Any
from enum import Enum


class Color(Enum):
    """颜色定义"""
    # 基础颜色
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    
    # 亮色
    BRIGHT_BLACK = "bright_black"
    BRIGHT_RED = "bright_red"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_WHITE = "bright_white"
    
    # 自定义颜色
    GRAY = "gray"
    DARK_GRAY = "dark_gray"
    LIGHT_GRAY = "light_gray"
    ORANGE = "orange"
    PURPLE = "purple"
    PINK = "pink"
    BROWN = "brown"


class Style(Enum):
    """样式定义"""
    NORMAL = "normal"
    BOLD = "bold"
    DIM = "dim"
    ITALIC = "italic"
    UNDERLINE = "underline"
    BLINK = "blink"
    REVERSE = "reverse"
    STRIKETHROUGH = "strikethrough"


class Theme:
    """主题类"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.colors = self._get_default_colors()
        self.styles = self._get_default_styles()
    
    def _get_default_colors(self) -> Dict[str, str]:
        """获取默认颜色配置"""
        return {
            # 背景色
            "background": Color.BLACK.value,
            "surface": Color.BRIGHT_BLACK.value,
            "panel": Color.BRIGHT_BLACK.value,
            
            # 前景色
            "foreground": Color.WHITE.value,
            "text": Color.WHITE.value,
            "text_secondary": Color.GRAY.value,
            "text_muted": Color.DARK_GRAY.value,
            
            # 状态色
            "success": Color.GREEN.value,
            "warning": Color.YELLOW.value,
            "error": Color.RED.value,
            "info": Color.BLUE.value,
            
            # 交互色
            "primary": Color.BLUE.value,
            "secondary": Color.CYAN.value,
            "accent": Color.MAGENTA.value,
            
            # 边框色
            "border": Color.GRAY.value,
            "border_focused": Color.BRIGHT_WHITE.value,
            "border_selected": Color.BLUE.value,
            
            # 特殊色
            "highlight": Color.BRIGHT_YELLOW.value,
            "selection": Color.BLUE.value,
            "cursor": Color.WHITE.value,
        }
    
    def _get_default_styles(self) -> Dict[str, str]:
        """获取默认样式配置"""
        return {
            "normal": Style.NORMAL.value,
            "bold": Style.BOLD.value,
            "italic": Style.ITALIC.value,
            "underline": Style.UNDERLINE.value,
            "dim": Style.DIM.value,
        }
    
    def get_color(self, name: str) -> str:
        """获取颜色值"""
        return self.colors.get(name, Color.WHITE.value)
    
    def get_style(self, name: str) -> str:
        """获取样式值"""
        return self.styles.get(name, Style.NORMAL.value)
    
    def set_color(self, name: str, color: str) -> None:
        """设置颜色"""
        self.colors[name] = color
    
    def set_style(self, name: str, style: str) -> None:
        """设置样式"""
        self.styles[name] = style


# 预定义主题
class Themes:
    """预定义主题集合"""
    
    @staticmethod
    def get_default_theme() -> Theme:
        """获取默认主题"""
        return Theme("default")
    
    @staticmethod
    def get_dark_theme() -> Theme:
        """获取深色主题"""
        theme = Theme("dark")
        theme.set_color("background", Color.BLACK.value)
        theme.set_color("surface", Color.BRIGHT_BLACK.value)
        theme.set_color("foreground", Color.WHITE.value)
        theme.set_color("text", Color.WHITE.value)
        theme.set_color("text_secondary", Color.GRAY.value)
        return theme
    
    @staticmethod
    def get_light_theme() -> Theme:
        """获取浅色主题"""
        theme = Theme("light")
        theme.set_color("background", Color.WHITE.value)
        theme.set_color("surface", Color.LIGHT_GRAY.value)
        theme.set_color("foreground", Color.BLACK.value)
        theme.set_color("text", Color.BLACK.value)
        theme.set_color("text_secondary", Color.DARK_GRAY.value)
        return theme
    
    @staticmethod
    def get_monokai_theme() -> Theme:
        """获取 Monokai 主题"""
        theme = Theme("monokai")
        theme.set_color("background", "#272822")
        theme.set_color("surface", "#3E3D32")
        theme.set_color("foreground", "#F8F8F2")
        theme.set_color("text", "#F8F8F2")
        theme.set_color("text_secondary", "#75715E")
        theme.set_color("primary", "#66D9EF")
        theme.set_color("success", "#A6E22E")
        theme.set_color("warning", "#E6DB74")
        theme.set_color("error", "#F92672")
        return theme
    
    @staticmethod
    def get_github_theme() -> Theme:
        """获取 GitHub 主题"""
        theme = Theme("github")
        theme.set_color("background", "#FFFFFF")
        theme.set_color("surface", "#F6F8FA")
        theme.set_color("foreground", "#24292E")
        theme.set_color("text", "#24292E")
        theme.set_color("text_secondary", "#586069")
        theme.set_color("primary", "#0366D6")
        theme.set_color("success", "#28A745")
        theme.set_color("warning", "#FFC107")
        theme.set_color("error", "#DC3545")
        return theme


# 全局主题实例
current_theme = Themes.get_default_theme()


def get_current_theme() -> Theme:
    """获取当前主题"""
    return current_theme


def set_theme(theme: Theme) -> None:
    """设置当前主题"""
    global current_theme
    current_theme = theme


def get_color(name: str) -> str:
    """获取当前主题的颜色"""
    return current_theme.get_color(name)


def get_style(name: str) -> str:
    """获取当前主题的样式"""
    return current_theme.get_style(name)
