#!/usr/bin/env python3
"""
命令系统演示程序 (Command System Demo)

功能说明:
- 演示如何使用命令管理器和各种命令
- 提供命令系统的使用示例和测试环境
- 注册并测试保存、加载、切换项目、帮助等命令
- 模拟用户输入，展示命令系统的交互流程

包含的演示功能:
1. 命令注册流程演示
2. 命令执行流程演示
3. 用户交互循环模拟
4. 普通输入与命令输入的区分处理

作用:
为开发者提供命令系统的使用参考，也可用于独立测试
各个命令的功能是否正常工作。
"""

from commands.command_manager import CommandManager
from commands.help_command import HelpCommand
from commands.save_command import SaveCommand
from commands.load_command import LoadCommand
from commands.switch_command import SwitchProjectCommand


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
    