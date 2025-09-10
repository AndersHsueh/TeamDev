from commands.command_base import CommandBase


class LoadCommand(CommandBase):
    def __init__(self):
        super().__init__("load", "加载指定项目", need_confirm=False)

    def execute(self, args: str) -> str:
        if not args:
            return "⚠️ 用法: /load <project_id>"
        return f"📂 已加载项目: {args}"

        