#!/usr/bin/env python3
"""
项目切换命令模块 (Switch Project Command Module)

功能说明:
- 实现/switch命令，用于在多个项目之间快速切换
- 提供项目选择界面，让用户从可用项目中选择
- 切换当前工作环境到指定项目
- 在TUI界面中可以集成项目选择菜单
- 集成新的项目状态管理系统

核心功能:
1. 获取系统中所有可用的项目列表
2. 提供项目选择机制
3. 执行项目环境切换逻辑
4. 更新当前活动项目的状态
5. 保持项目状态的持久化

作用:
为多项目工作流提供便捷的切换机制，
提高用户在不同项目间工作的效率。
"""

import logging
from commands.command_base import CommandBase
from core.project_manager import switch_project_interactive, current_project_manager

logger = logging.getLogger(__name__)


class SwitchProjectCommand(CommandBase):
    def __init__(self):
        super().__init__("switch", "切换当前项目", need_confirm=False)

    def execute(self, args: str) -> str:
        """
        执行项目切换命令
        
        Args:
            args: 命令参数（暂时未使用）
            
        Returns:
            str: 执行结果信息
        """
        try:
            # 显示当前项目信息
            current_project = current_project_manager.current_project
            if current_project:
                result = f"当前项目: {current_project.name}\n"
                result += f"项目路径: {current_project.path}\n\n"
            else:
                result = "当前没有选择项目\n\n"
            
            # 执行项目切换
            if switch_project_interactive():
                new_project = current_project_manager.current_project
                if new_project:
                    result += f"🔀 已成功切换到项目: {new_project.name}\n"
                    result += f"项目路径: {new_project.path}"
                    logger.info(f"命令行切换项目成功: {new_project.name}")
                else:
                    result += "⚠️ 项目切换后状态异常"
                    logger.warning("项目切换后状态异常")
            else:
                result += "❌ 项目切换已取消或失败"
                logger.info("用户取消项目切换")
            
            return result
            
        except Exception as e:
            error_msg = f"❌ 项目切换失败: {str(e)}"
            logger.error(f"项目切换失败: {e}")
            return error_msg

    def get_help(self) -> str:
        """获取命令帮助信息"""
        return """
命令: /switch 或 /s

功能: 切换当前工作项目

使用方法:
  /switch    - 显示项目选择菜单并切换项目
  /s         - 简写形式

说明:
- 会显示当前项目信息
- 弹出项目选择对话框
- 支持选择现有项目或创建新项目
- 切换后会自动保存项目状态

示例:
  /switch
  /s
"""


class SwitchCommand(SwitchProjectCommand):
    """为了兼容性保留的别名类"""
    def __init__(self):
        super().__init__()
        self.name = "switch_project"  # 保持原有名称兼容性

        