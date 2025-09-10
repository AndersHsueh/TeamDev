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
        