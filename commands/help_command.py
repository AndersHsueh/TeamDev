#!/usr/bin/env python3
"""
帮助命令模块 (Help Command Module)

功能说明:
- 实现/help命令，显示系统中所有可用命令的帮助信息
- 动态获取命令管理器中注册的所有命令
- 格式化输出每个命令的名称和描述
- 为用户提供命令系统的使用指南

核心功能:
1. 遍历命令管理器中的所有已注册命令
2. 调用每个命令的help()方法获取帮助文本
3. 统一格式化并返回完整的帮助信息

作用:
作为用户了解系统功能的入口，帮助用户快速掌握
可用的命令和使用方法。
"""

from commands.command_base import CommandBase


class HelpCommand(CommandBase):
    def __init__(self, manager):
        super().__init__("help", "显示帮助信息")
        self.manager = manager

    def execute(self, args: str) -> str:
        lines = ["支持的命令:"]
        for cmd in self.manager.commands.values():
            lines.append(f"  {cmd.help()}")
        return "\n".join(lines)
        