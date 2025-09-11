"""
角色系统基础抽象类
定义统一的角色行为接口
"""

import abc
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class RoleContext:
    """角色执行上下文"""
    user_input: str
    conversation_history: List[Dict[str, str]]
    project_info: Optional[Dict[str, Any]] = None
    session_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.project_info is None:
            self.project_info = {}
        if self.session_data is None:
            self.session_data = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RoleAction:
    """角色执行结果"""
    response: str
    actions: List[Dict[str, Any]] = None  # 要执行的工具调用
    metadata: Optional[Dict[str, Any]] = None
    should_continue: bool = True

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.metadata is None:
            self.metadata = {}


class Role(abc.ABC):
    """
    角色抽象基类

    所有角色都需要实现这个接口，确保统一的行为模式
    """

    def __init__(self, name: str, llm_provider: LLMProvider, config: Optional[Dict[str, Any]] = None):
        """
        初始化角色

        Args:
            name: 角色名称
            llm_provider: LLM 提供商实例
            config: 角色特定配置
        """
        self.name = name
        self.llm_provider = llm_provider
        self.config = config or {}

        # 角色状态
        self.is_active = True
        self.last_action_time = 0.0

        # 角色特定的系统提示
        self.system_prompt = self._get_system_prompt()

        logger.info(f"角色 {name} 已初始化")

    @abc.abstractmethod
    def act(self, context: RoleContext) -> RoleAction:
        """
        执行角色行为

        Args:
            context: 执行上下文

        Returns:
            RoleAction: 执行结果
        """
        pass

    @abc.abstractmethod
    def _get_system_prompt(self) -> str:
        """
        获取角色特定的系统提示

        Returns:
            str: 系统提示文本
        """
        pass

    def get_capabilities(self) -> List[str]:
        """
        获取角色的能力列表

        Returns:
            List[str]: 能力描述列表
        """
        return []

    def can_handle(self, user_input: str) -> bool:
        """
        判断角色是否能处理给定的输入

        Args:
            user_input: 用户输入

        Returns:
            bool: True 如果能处理，否则 False
        """
        return True  # 默认所有角色都能处理输入

    def preprocess_input(self, user_input: str) -> str:
        """
        预处理用户输入

        Args:
            user_input: 原始用户输入

        Returns:
            str: 处理后的输入
        """
        return user_input.strip()

    def postprocess_output(self, response: str) -> str:
        """
        后处理响应输出

        Args:
            response: 原始响应

        Returns:
            str: 处理后的响应
        """
        return response.strip()

    def _call_llm(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        调用 LLM 生成响应

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            LLMResponse: LLM 响应
        """
        try:
            # 添加系统提示
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages

            response = self.llm_provider.generate(full_messages, **kwargs)

            if response.error:
                logger.error(f"角色 {self.name} LLM 调用失败: {response.error}")
                # 返回错误信息作为响应
                response.content = f"抱歉，我遇到了一些问题：{response.error}"

            return response

        except Exception as e:
            logger.error(f"角色 {self.name} 调用 LLM 时发生异常: {e}")
            return LLMResponse(
                content=f"抱歉，处理您的请求时发生错误：{str(e)}",
                model=self.llm_provider.model,
                error=str(e)
            )

    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """
        从响应中提取要执行的动作

        Args:
            response: LLM 响应文本

        Returns:
            List[Dict[str, Any]]: 动作列表
        """
        actions = []

        # 这里可以实现更复杂的动作提取逻辑
        # 目前返回空列表，子类可以重写这个方法

        return actions

    def update_config(self, new_config: Dict[str, Any]):
        """
        更新角色配置

        Args:
            new_config: 新的配置字典
        """
        self.config.update(new_config)
        logger.info(f"角色 {self.name} 配置已更新")

    def deactivate(self):
        """停用角色"""
        self.is_active = False
        logger.info(f"角色 {self.name} 已停用")

    def activate(self):
        """激活角色"""
        self.is_active = True
        logger.info(f"角色 {self.name} 已激活")

    @property
    def status(self) -> str:
        """角色状态"""
        return "active" if self.is_active else "inactive"
