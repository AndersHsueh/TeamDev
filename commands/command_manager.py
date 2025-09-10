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
        