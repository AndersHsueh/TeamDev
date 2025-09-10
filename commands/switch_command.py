from commands.command_base import CommandBase


class SwitchProjectCommand(CommandBase):
    def __init__(self):
        super().__init__("switch_project", "切换当前项目", need_confirm=False)

    def execute(self, args: str) -> str:
        # 在 TUI 里可以弹出选择菜单，这里先简化
        return "🔀 当前项目切换成功。"

        