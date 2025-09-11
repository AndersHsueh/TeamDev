"""
LLM Provider 基础抽象类
定义统一的 LLM 调用接口
"""

import abc
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM 响应数据结构"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0
    error: Optional[str] = None

    def __post_init__(self):
        if self.usage is None:
            self.usage = {}


@dataclass
class LLMConfig:
    """LLM 配置数据结构"""
    name: str
    type: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


class LLMProvider(abc.ABC):
    """
    LLM Provider 抽象基类

    所有 LLM 提供商都需要实现这个接口，确保统一的调用方式。
    """

    def __init__(self, config: LLMConfig):
        """
        初始化 LLM Provider

        Args:
            config: LLM 配置信息
        """
        self.config = config
        self._last_request_time = 0.0

    @abc.abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        生成响应

        Args:
            messages: 消息列表，格式如：
                [{"role": "user", "content": "Hello"}]
            **kwargs: 额外的参数，会覆盖配置中的参数

        Returns:
            LLMResponse: 生成的响应
        """
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """
        检查提供商是否可用

        Returns:
            bool: True 如果可用，否则 False
        """
        pass

    def _merge_params(self, **kwargs) -> Dict[str, Any]:
        """
        合并参数：配置参数 + 运行时参数

        Args:
            **kwargs: 运行时参数

        Returns:
            Dict[str, Any]: 合并后的参数
        """
        params = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout,
        }

        # 合并额外配置参数
        if self.config.extra_params:
            params.update(self.config.extra_params)

        # 运行时参数覆盖配置参数
        params.update(kwargs)

        # 清理 None 值
        return {k: v for k, v in params.items() if v is not None}

    def _record_request_time(self):
        """记录请求时间，用于限流"""
        self._last_request_time = time.time()

    def get_rate_limit_delay(self) -> float:
        """
        获取请求间隔时间（用于限流）

        Returns:
            float: 建议的延迟时间（秒）
        """
        # 默认没有限流
        return 0.0

    @property
    def name(self) -> str:
        """提供商名称"""
        return self.config.name

    @property
    def model(self) -> str:
        """模型名称"""
        return self.config.model_name or "unknown"
