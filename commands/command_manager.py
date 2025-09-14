#!/usr/bin/env python3
"""
命令管理器模块 (Command Manager Module)

功能说明:
- 负责注册、管理和执行系统中的所有命令
- 解析用户输入的命令格式（/命令名 参数）
- 路由命令到对应的处理器执行
- 处理未知命令的错误情况
- 支持需要用户确认的命令

核心功能:
1. register() - 注册新命令到管理器
2. execute() - 解析并执行用户输入的命令
3. 统一的命令调度和错误处理机制

作用:
作为命令系统的核心调度器，统一管理所有命令的注册和执行，
为TUI界面提供简洁的命令执行接口。
"""

from typing import Dict
from commands.command_base import CommandBase


class CommandManager:
    def __init__(self):
        self.commands: Dict[str, CommandBase] = {}

    def register(self, command: CommandBase):
        """注册一个命令"""
        self.commands[command.name] = command

    def execute(self, input_str: str) -> str:
        """执行命令"""
        if not input_str.startswith("/"):
            raise ValueError("不是命令")

        parts = input_str[1:].split(maxsplit=1)
        cmd_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        cmd = self.commands.get(cmd_name)
        if not cmd:
            return f"❓ 未知命令: /{cmd_name}. 输入 /help 查看支持的命令。"

        if cmd.need_confirm:
            # 这里只返回提示，实际确认逻辑可以在外层处理
            return f"⚠️ 确认执行 /{cmd_name} ? (y/n)"

        return cmd.execute(args)
        