#!/usr/bin/env python3
"""
命令系统初始化模块

负责初始化和注册所有系统命令
"""

import logging
from commands.command_manager import CommandManager
from commands.help_command import HelpCommand
from commands.save_command import SaveCommand
from commands.load_command import LoadCommand
from commands.switch_command import SwitchProjectCommand, SwitchCommand
from commands.project_command import ProjectCommand, PCommand

logger = logging.getLogger(__name__)


def create_command_manager() -> CommandManager:
    """
    创建并初始化命令管理器
    
    Returns:
        CommandManager: 已注册所有命令的管理器
    """
    manager = CommandManager()
    
    # 注册所有命令
    manager.register(HelpCommand(manager))
    manager.register(SaveCommand())
    manager.register(LoadCommand())
    
    # 项目管理命令
    manager.register(ProjectCommand())
    manager.register(PCommand())  # 简写形式
    
    # 项目切换命令
    manager.register(SwitchProjectCommand())
    manager.register(SwitchCommand())  # 兼容性别名
    
    logger.info(f"已注册 {len(manager.commands)} 个命令")
    return manager


def get_command_help() -> str:
    """
    获取所有命令的帮助信息
    
    Returns:
        str: 格式化的帮助信息
    """
    manager = create_command_manager()
    help_command = manager.commands.get('help')
    
    if help_command:
        return help_command.execute('')
    else:
        return "帮助系统不可用"


# 全局命令管理器实例
_global_command_manager = None


def get_global_command_manager() -> CommandManager:
    """
    获取全局命令管理器实例
    
    Returns:
        CommandManager: 全局命令管理器
    """
    global _global_command_manager
    
    if _global_command_manager is None:
        _global_command_manager = create_command_manager()
        logger.info("全局命令管理器已初始化")
    
    return _global_command_manager


if __name__ == "__main__":
    # 测试命令系统
    manager = create_command_manager()
    
    print("=== TeamDev 命令系统测试 ===")
    print(f"已注册 {len(manager.commands)} 个命令:")
    
    for cmd_name, cmd in manager.commands.items():
        print(f"  - /{cmd_name}: {cmd.description}")
    
    print("\n=== 测试帮助命令 ===")
    print(manager.execute("/help"))
    
    print("\n=== 测试项目命令 ===")
    print(manager.execute("/project"))