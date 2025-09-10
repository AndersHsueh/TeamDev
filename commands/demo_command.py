from commands.command_manager import CommandManager
from commands.help_command import HelpCommand
from commands.save_command import SaveCommand
from commands.load_command import LoadCommand
from commands.switch_project import SwitchProjectCommand


def main():
    manager = CommandManager()

    # 注册命令
    manager.register(SaveCommand())
    manager.register(LoadCommand())
    manager.register(SwitchProjectCommand())
    manager.register(HelpCommand(manager))  # 注意传入 manager

    # 模拟输入
    while True:
        user_input = input("> ")
        if user_input == "exit":
            break

        if user_input.startswith("/"):
            output = manager.execute(user_input)
            print(output)
        else:
            print(f"普通输入: {user_input}")


if __name__ == "__main__":
    main()
    