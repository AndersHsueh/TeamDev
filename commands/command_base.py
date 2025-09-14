#!/usr/bin/env python3
"""
命令基类模块 (Command Base Module)

功能说明:
- 定义了所有命令的抽象基类 CommandBase
- 为所有命令提供统一的接口和基本属性
- 包含命令名称、描述、是否需要确认等基本属性
- 定义了execute()抽象方法供子类实现具体的命令逻辑
- 提供默认的help()方法返回命令帮助信息

作用:
作为命令系统的基础架构，确保所有命令实现都遵循统一的接口规范，
便于命令管理器统一调度和管理各种命令。
"""

from abc import ABC, abstractmethod


class CommandBase(ABC):
    def __init__(self, name: str, description: str, need_confirm: bool = False):
        self.name = name
        self.description = description
        self.need_confirm = need_confirm

    @abstractmethod
    def execute(self, args: str) -> str:
        """执行命令逻辑"""
        pass

    def help(self) -> str:
        """默认帮助信息"""
        return f"/{self.name} : {self.description}"
        