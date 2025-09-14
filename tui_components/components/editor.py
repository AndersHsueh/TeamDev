"""
文本/代码编辑器组件
支持语法高亮、行号显示、搜索等功能
"""

import re
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from ..core.base_component import BaseComponent
from ..core.theme import get_color, get_style


@dataclass
class Position:
    """光标位置"""
    line: int
    column: int


@dataclass
class Selection:
    """选择区域"""
    start: Position
    end: Position
    
    def is_empty(self) -> bool:
        """是否为空选择"""
        return self.start.line == self.end.line and self.start.column == self.end.column
    
    def normalize(self) -> 'Selection':
        """标准化选择区域（确保 start <= end）"""
        if (self.start.line > self.end.line or 
            (self.start.line == self.end.line and self.start.column > self.end.column)):
            return Selection(self.end, self.start)
        return self


class EditorComponent(BaseComponent):
    """文本/代码编辑器组件"""
    
    def __init__(self, *, id: str | None = None, classes: str | None = None, name: str | None = None):
        super().__init__(id=id, classes=classes, name=name)
        self.lines: List[str] = [""]  # 文本行
        self.cursor = Position(0, 0)  # 光标位置
        self.selection = Selection(Position(0, 0), Position(0, 0))  # 选择区域
        self.scroll_line = 0  # 滚动行偏移
        self.scroll_column = 0  # 滚动列偏移
        self.show_line_numbers = True
        self.show_ruler = False
        self.ruler_column = 80
        self.tab_size = 4
        self.use_spaces = True  # 使用空格代替制表符
        self.word_wrap = False
        self.read_only = False
        self.syntax_highlighting = True
        self.language = "text"
        
        # 搜索相关
        self.search_text = ""
        self.search_case_sensitive = False
        self.search_regex = False
        self.search_matches: List[Tuple[int, int, int]] = []  # (line, start, end)
        self.current_match = -1
        
        # 回调函数
        self.on_text_changed: Optional[Callable[[str], None]] = None
        self.on_cursor_moved: Optional[Callable[[Position], None]] = None
        self.on_selection_changed: Optional[Callable[[Selection], None]] = None
        
        # 语法高亮配置
        self.syntax_patterns = self._get_default_syntax_patterns()
    
    def _get_default_syntax_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """获取默认语法高亮模式"""
        return {
            "python": [
                (r'\b(def|class|if|else|elif|for|while|try|except|finally|with|import|from|return|yield|lambda)\b', 'keyword'),
                (r'\b(True|False|None)\b', 'constant'),
                (r'"[^"]*"', 'string'),
                (r"'[^']*'", 'string'),
                (r'#.*$', 'comment'),
                (r'\b\d+\.?\d*\b', 'number'),
            ],
            "javascript": [
                (r'\b(function|var|let|const|if|else|for|while|try|catch|finally|return|class|extends|import|export)\b', 'keyword'),
                (r'\b(true|false|null|undefined)\b', 'constant'),
                (r'"[^"]*"', 'string'),
                (r"'[^']*'", 'string'),
                (r'//.*$', 'comment'),
                (r'/\*.*?\*/', 'comment'),
                (r'\b\d+\.?\d*\b', 'number'),
            ],
            "text": [],
        }
    
    def set_text(self, text: str) -> None:
        """设置文本内容"""
        self.lines = text.split('\n') if text else [""]
        self.cursor = Position(0, 0)
        self.selection = Selection(Position(0, 0), Position(0, 0))
        self.scroll_line = 0
        self.scroll_column = 0
        self._trigger_text_changed()
    
    def get_text(self) -> str:
        """获取文本内容"""
        return '\n'.join(self.lines)
    
    def insert_text(self, text: str) -> None:
        """插入文本"""
        if self.read_only:
            return
        
        if not self.selection.is_empty():
            self._delete_selection()
        
        # 在光标位置插入文本
        line = self.lines[self.cursor.line]
        before_cursor = line[:self.cursor.column]
        after_cursor = line[self.cursor.column:]
        
        if '\n' in text:
            # 多行文本
            lines = text.split('\n')
            self.lines[self.cursor.line] = before_cursor + lines[0]
            
            # 插入中间行
            for i in range(1, len(lines) - 1):
                self.lines.insert(self.cursor.line + i, lines[i])
            
            # 插入最后一行
            if len(lines) > 1:
                self.lines.insert(self.cursor.line + len(lines) - 1, lines[-1] + after_cursor)
            
            # 更新光标位置
            self.cursor.line += len(lines) - 1
            self.cursor.column = len(lines[-1])
        else:
            # 单行文本
            self.lines[self.cursor.line] = before_cursor + text + after_cursor
            self.cursor.column += len(text)
        
        self._trigger_text_changed()
        self._trigger_cursor_moved()
    
    def delete_char(self, forward: bool = True) -> None:
        """删除字符"""
        if self.read_only:
            return
        
        if not self.selection.is_empty():
            self._delete_selection()
            return
        
        if forward:
            # 删除光标后的字符
            if self.cursor.column < len(self.lines[self.cursor.line]):
                # 删除当前行的字符
                line = self.lines[self.cursor.line]
                self.lines[self.cursor.line] = line[:self.cursor.column] + line[self.cursor.column + 1:]
            elif self.cursor.line < len(self.lines) - 1:
                # 合并到下一行
                current_line = self.lines[self.cursor.line]
                next_line = self.lines[self.cursor.line + 1]
                self.lines[self.cursor.line] = current_line + next_line
                del self.lines[self.cursor.line + 1]
        else:
            # 删除光标前的字符
            if self.cursor.column > 0:
                # 删除当前行的字符
                line = self.lines[self.cursor.line]
                self.lines[self.cursor.line] = line[:self.cursor.column - 1] + line[self.cursor.column:]
                self.cursor.column -= 1
            elif self.cursor.line > 0:
                # 合并到上一行
                prev_line = self.lines[self.cursor.line - 1]
                current_line = self.lines[self.cursor.line]
                self.lines[self.cursor.line - 1] = prev_line + current_line
                del self.lines[self.cursor.line]
                self.cursor.line -= 1
                self.cursor.column = len(prev_line)
        
        self._trigger_text_changed()
        self._trigger_cursor_moved()
    
    def _delete_selection(self) -> None:
        """删除选择区域"""
        if self.selection.is_empty():
            return
        
        sel = self.selection.normalize()
        
        if sel.start.line == sel.end.line:
            # 单行选择
            line = self.lines[sel.start.line]
            self.lines[sel.start.line] = line[:sel.start.column] + line[sel.end.column:]
            self.cursor = sel.start
        else:
            # 多行选择
            start_line = self.lines[sel.start.line]
            end_line = self.lines[sel.end.line]
            
            # 合并首尾行
            self.lines[sel.start.line] = start_line[:sel.start.column] + end_line[sel.end.column:]
            
            # 删除中间行
            del self.lines[sel.start.line + 1:sel.end.line + 1]
            
            self.cursor = sel.start
        
        self.selection = Selection(Position(0, 0), Position(0, 0))
    
    def move_cursor(self, line: int, column: int) -> None:
        """移动光标"""
        # 限制光标位置
        line = max(0, min(line, len(self.lines) - 1))
        column = max(0, min(column, len(self.lines[line])))
        
        self.cursor = Position(line, column)
        self._trigger_cursor_moved()
    
    def move_cursor_relative(self, delta_line: int, delta_column: int) -> None:
        """相对移动光标"""
        new_line = self.cursor.line + delta_line
        new_column = self.cursor.column + delta_column
        
        self.move_cursor(new_line, new_column)
    
    def set_selection(self, start: Position, end: Position) -> None:
        """设置选择区域"""
        self.selection = Selection(start, end)
        self._trigger_selection_changed()
    
    def select_all(self) -> None:
        """全选"""
        if self.lines:
            start = Position(0, 0)
            end = Position(len(self.lines) - 1, len(self.lines[-1]))
            self.set_selection(start, end)
    
    def search(self, text: str, case_sensitive: bool = False, regex: bool = False) -> int:
        """搜索文本"""
        self.search_text = text
        self.search_case_sensitive = case_sensitive
        self.search_regex = regex
        
        self.search_matches.clear()
        
        if not text:
            return 0
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for line_idx, line in enumerate(self.lines):
            if regex:
                try:
                    pattern = re.compile(text, flags)
                    for match in pattern.finditer(line):
                        self.search_matches.append((line_idx, match.start(), match.end()))
                except re.error:
                    pass
            else:
                search_text = text if case_sensitive else text.lower()
                line_text = line if case_sensitive else line.lower()
                
                start = 0
                while True:
                    pos = line_text.find(search_text, start)
                    if pos == -1:
                        break
                    self.search_matches.append((line_idx, pos, pos + len(text)))
                    start = pos + 1
        
        self.current_match = 0 if self.search_matches else -1
        return len(self.search_matches)
    
    def goto_next_match(self) -> bool:
        """跳转到下一个匹配"""
        if not self.search_matches:
            return False
        
        self.current_match = (self.current_match + 1) % len(self.search_matches)
        line, start, end = self.search_matches[self.current_match]
        
        self.move_cursor(line, start)
        self.set_selection(Position(line, start), Position(line, end))
        
        # 确保匹配可见
        self._ensure_cursor_visible()
        
        return True
    
    def goto_prev_match(self) -> bool:
        """跳转到上一个匹配"""
        if not self.search_matches:
            return False
        
        self.current_match = (self.current_match - 1) % len(self.search_matches)
        line, start, end = self.search_matches[self.current_match]
        
        self.move_cursor(line, start)
        self.set_selection(Position(line, start), Position(line, end))
        
        # 确保匹配可见
        self._ensure_cursor_visible()
        
        return True
    
    def _ensure_cursor_visible(self) -> None:
        """确保光标可见"""
        # 调整垂直滚动
        if self.cursor.line < self.scroll_line:
            self.scroll_line = self.cursor.line
        elif self.cursor.line >= self.scroll_line + self.size.height:
            self.scroll_line = self.cursor.line - self.size.height + 1
        
        # 调整水平滚动
        line_width = len(self.lines[self.cursor.line])
        if self.cursor.column < self.scroll_column:
            self.scroll_column = self.cursor.column
        elif self.cursor.column >= self.scroll_column + self.size.width - (10 if self.show_line_numbers else 0):
            self.scroll_column = self.cursor.column - self.size.width + (10 if self.show_line_numbers else 0) + 1
    
    def _trigger_text_changed(self) -> None:
        """触发文本变化事件"""
        if self.on_text_changed:
            self.on_text_changed(self.get_text())
    
    def _trigger_cursor_moved(self) -> None:
        """触发光标移动事件"""
        if self.on_cursor_moved:
            self.on_cursor_moved(self.cursor)
    
    def _trigger_selection_changed(self) -> None:
        """触发选择变化事件"""
        if self.on_selection_changed:
            self.on_selection_changed(self.selection)
    
    def render(self) -> str:
        """渲染组件内容"""
        if not self.visible:
            return ""
        
        lines = []
        
        # 计算显示范围
        start_line = self.scroll_line
        end_line = min(start_line + self.size.height, len(self.lines))
        
        for i in range(start_line, end_line):
            line_num = i + 1
            line_content = self.lines[i]
            
            # 构建行内容
            display_line = self._render_line(line_num, line_content, i)
            lines.append(display_line)
        
        # 填充剩余行
        while len(lines) < self.size.height:
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_line(self, line_num: int, content: str, line_idx: int) -> str:
        """渲染单行"""
        # 行号
        line_number = ""
        if self.show_line_numbers:
            line_number = f"{line_num:4d} "
        
        # 内容
        display_content = content[self.scroll_column:]
        
        # 应用语法高亮
        if self.syntax_highlighting and self.language in self.syntax_patterns:
            display_content = self._apply_syntax_highlighting(display_content)
        
        # 应用选择高亮
        if not self.selection.is_empty():
            display_content = self._apply_selection_highlighting(display_content, line_idx)
        
        # 应用搜索高亮
        if self.search_matches:
            display_content = self._apply_search_highlighting(display_content, line_idx)
        
        # 截断过长的行
        max_width = self.size.width - len(line_number)
        if len(display_content) > max_width:
            display_content = display_content[:max_width-3] + "..."
        
        return line_number + display_content
    
    def _apply_syntax_highlighting(self, text: str) -> str:
        """应用语法高亮"""
        if self.language not in self.syntax_patterns:
            return text
        
        highlighted = text
        patterns = self.syntax_patterns[self.language]
        
        for pattern, style in patterns:
            if style == 'keyword':
                color = get_color("primary")
            elif style == 'string':
                color = get_color("success")
            elif style == 'comment':
                color = get_color("text_muted")
            elif style == 'number':
                color = get_color("warning")
            elif style == 'constant':
                color = get_color("accent")
            else:
                color = get_color("text")
            
            highlighted = re.sub(pattern, f"[{color}]\\g<0>[/{color}]", highlighted)
        
        return highlighted
    
    def _apply_selection_highlighting(self, text: str, line_idx: int) -> str:
        """应用选择高亮"""
        if self.selection.is_empty():
            return text
        
        sel = self.selection.normalize()
        
        if sel.start.line <= line_idx <= sel.end.line:
            start_col = sel.start.column if line_idx == sel.start.line else 0
            end_col = sel.end.column if line_idx == sel.end.line else len(text)
            
            if start_col < len(text) and end_col > 0:
                before = text[:start_col]
                selected = text[start_col:end_col]
                after = text[end_col:]
                
                selection_color = get_color("selection")
                return f"{before}[{selection_color}]{selected}[/{selection_color}]{after}"
        
        return text
    
    def _apply_search_highlighting(self, text: str, line_idx: int) -> str:
        """应用搜索高亮"""
        highlighted = text
        
        for match_line, match_start, match_end in self.search_matches:
            if match_line == line_idx:
                # 调整匹配位置（考虑滚动偏移）
                adj_start = max(0, match_start - self.scroll_column)
                adj_end = max(0, match_end - self.scroll_column)
                
                if adj_start < len(highlighted) and adj_end > 0:
                    before = highlighted[:adj_start]
                    matched = highlighted[adj_start:adj_end]
                    after = highlighted[adj_end:]
                    
                    highlight_color = get_color("highlight")
                    highlighted = f"{before}[{highlight_color}]{matched}[/{highlight_color}]{after}"
        
        return highlighted
    
    def update(self, data: Any = None) -> None:
        """更新组件状态"""
        if isinstance(data, dict):
            if "text" in data:
                self.set_text(data["text"])
            if "read_only" in data:
                self.read_only = data["read_only"]
            if "show_line_numbers" in data:
                self.show_line_numbers = data["show_line_numbers"]
            if "language" in data:
                self.language = data["language"]
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        if not self.visible:
            return False
        
        if self.read_only and key not in ["up", "down", "left", "right", "page_up", "page_down", "home", "end"]:
            return False
        
        # 移动光标
        if key == "up" or key == "k":
            self.move_cursor_relative(-1, 0)
            return True
        elif key == "down" or key == "j":
            self.move_cursor_relative(1, 0)
            return True
        elif key == "left" or key == "h":
            self.move_cursor_relative(0, -1)
            return True
        elif key == "right" or key == "l":
            self.move_cursor_relative(0, 1)
            return True
        
        # 快速移动
        elif key == "ctrl+left" or key == "ctrl+h":
            # 移动到单词开始
            self._move_to_word_start()
            return True
        elif key == "ctrl+right" or key == "ctrl+l":
            # 移动到单词结束
            self._move_to_word_end()
            return True
        elif key == "home":
            # 移动到行首
            self.move_cursor(self.cursor.line, 0)
            return True
        elif key == "end":
            # 移动到行尾
            self.move_cursor(self.cursor.line, len(self.lines[self.cursor.line]))
            return True
        
        # 页面滚动
        elif key == "page_up" or key == "ctrl+u":
            self.move_cursor_relative(-self.size.height // 2, 0)
            return True
        elif key == "page_down" or key == "ctrl+d":
            self.move_cursor_relative(self.size.height // 2, 0)
            return True
        
        # 编辑操作
        elif key == "backspace":
            self.delete_char(False)
            return True
        elif key == "delete":
            self.delete_char(True)
            return True
        elif key == "enter":
            self.insert_text("\n")
            return True
        elif key == "tab":
            indent = " " * self.tab_size if self.use_spaces else "\t"
            self.insert_text(indent)
            return True
        
        # 选择操作
        elif key == "ctrl+a":
            self.select_all()
            return True
        
        # 搜索操作
        elif key == "ctrl+f":
            # 这里应该触发搜索对话框，暂时跳过
            pass
        elif key == "f3":
            self.goto_next_match()
            return True
        elif key == "shift+f3":
            self.goto_prev_match()
            return True
        
        return False
    
    def _move_to_word_start(self) -> None:
        """移动到单词开始"""
        line = self.lines[self.cursor.line]
        col = self.cursor.column
        
        # 跳过当前单词
        while col > 0 and line[col - 1].isalnum():
            col -= 1
        
        # 跳过空白字符
        while col > 0 and line[col - 1].isspace():
            col -= 1
        
        self.move_cursor(self.cursor.line, col)
    
    def _move_to_word_end(self) -> None:
        """移动到单词结束"""
        line = self.lines[self.cursor.line]
        col = self.cursor.column
        
        # 跳过空白字符
        while col < len(line) and line[col].isspace():
            col += 1
        
        # 跳过当前单词
        while col < len(line) and line[col].isalnum():
            col += 1
        
        self.move_cursor(self.cursor.line, col)
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        if not self.visible:
            return False
        
        # 计算点击位置
        click_line = self.scroll_line + y
        click_column = self.scroll_column + x - (5 if self.show_line_numbers else 0)
        
        if 0 <= click_line < len(self.lines):
            self.move_cursor(click_line, click_column)
            return True
        
        return False
