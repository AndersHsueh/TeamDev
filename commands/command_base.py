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
        