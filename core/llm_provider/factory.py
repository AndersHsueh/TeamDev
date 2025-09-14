"""
LLM Provider 工厂模块

本模块实现了工厂模式，负责根据配置动态创建相应的 LLM Provider 实例。

核心功能：
- 工厂模式实现：根据配置类型动态创建不同的 Provider 实例
- 类型注册机制：通过 PROVIDER_TYPES 字典管理支持的 Provider 类型
- 配置验证：验证配置参数的完整性和有效性
- 统一创建接口：提供便捷的静态方法和函数接口

支持的 Provider 类型：
- openai: OpenAI GPT 系列模型
- ollama: 本地部署的 Ollama 模型
- mock: 测试和开发用的模拟 Provider

设计优势：
- 解耦创建逻辑：将对象创建从业务逻辑中分离
- 易于扩展：添加新的 Provider 类型只需修改类型映射
- 配置驱动：支持从配置文件动态创建实例
- 错误处理：完善的异常处理和日志记录
"""

import logging
from typing import Dict, Any, Optional

from .base import LLMProvider, LLMConfig
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .lmstudio_provider import LMStudioProvider
from .mock_provider import MockProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    LLM Provider 工厂类

    负责根据配置创建相应的 Provider 实例
    """

    # 支持的 provider 类型映射
    PROVIDER_TYPES = {
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "lmstudio": LMStudioProvider,
        "mock": MockProvider,
    }

    @classmethod
    def create_provider(cls, config: Dict[str, Any]) -> LLMProvider:
        """
        根据配置创建 Provider 实例

        Args:
            config: Provider 配置字典，格式如：
                {
                    "name": "gpt-4",
                    "type": "openai",
                    "api_key": "sk-...",
                    "model_name": "gpt-4",
                    "temperature": 0.7
                }

        Returns:
            LLMProvider: 创建的 Provider 实例

        Raises:
            ValueError: 当配置无效或不支持的类型时
        """
        try:
            # 验证必需字段
            if "name" not in config:
                raise ValueError("Provider 配置缺少 'name' 字段")

            if "type" not in config:
                raise ValueError("Provider 配置缺少 'type' 字段")

            provider_type = config["type"].lower()

            if provider_type not in cls.PROVIDER_TYPES:
                available_types = list(cls.PROVIDER_TYPES.keys())
                raise ValueError(f"不支持的 provider 类型: {provider_type}，可用类型: {available_types}")

            # 创建 LLMConfig 对象
            llm_config = cls._create_config_from_dict(config)

            # 创建 Provider 实例
            provider_class = cls.PROVIDER_TYPES[provider_type]
            provider = provider_class(llm_config)

            logger.info(f"成功创建 {provider_type} Provider: {config['name']}")
            return provider

        except Exception as e:
            logger.error(f"创建 Provider 失败: {e}")
            raise

    @classmethod
    def create_provider_from_config(cls, config_dict: Dict[str, Any]) -> LLMProvider:
        """
        从配置文件格式创建 Provider

        这是一个便捷方法，用于从 ai_settings.json 等配置文件创建

        Args:
            config_dict: 配置字典

        Returns:
            LLMProvider: 创建的 Provider 实例
        """
        return cls.create_provider(config_dict)

    @classmethod
    def get_available_types(cls) -> list:
        """
        获取所有可用的 Provider 类型

        Returns:
            list: 支持的类型列表
        """
        return list(cls.PROVIDER_TYPES.keys())

    @classmethod
    def is_type_supported(cls, provider_type: str) -> bool:
        """
        检查是否支持指定的 Provider 类型

        Args:
            provider_type: Provider 类型

        Returns:
            bool: True 如果支持，否则 False
        """
        return provider_type.lower() in cls.PROVIDER_TYPES

    @staticmethod
    def _create_config_from_dict(config_dict: Dict[str, Any]) -> LLMConfig:
        """
        从字典创建 LLMConfig 对象

        Args:
            config_dict: 配置字典

        Returns:
            LLMConfig: 配置对象
        """
        # 提取配置参数
        extra_params = {}

        # OpenAI 特定参数
        openai_params = ["top_p", "frequency_penalty", "presence_penalty", "stop"]
        for param in openai_params:
            if param in config_dict:
                extra_params[param] = config_dict[param]

        # Ollama 特定参数
        ollama_params = ["top_p", "top_k", "num_predict"]
        for param in ollama_params:
            if param in config_dict:
                extra_params[param] = config_dict[param]

        return LLMConfig(
            name=config_dict.get("name", "unnamed"),
            type=config_dict.get("type", "mock"),
            api_key=config_dict.get("api_key"),
            base_url=config_dict.get("base_url"),
            model_name=config_dict.get("model_name"),
            temperature=config_dict.get("temperature", 0.7),
            max_tokens=config_dict.get("max_tokens"),
            timeout=config_dict.get("timeout", 30),
            extra_params=extra_params if extra_params else None
        )


def create_provider(config: Dict[str, Any]) -> LLMProvider:
    """
    创建 Provider 的便捷函数

    Args:
        config: Provider 配置

    Returns:
        LLMProvider: 创建的 Provider 实例
    """
    return LLMProviderFactory.create_provider(config)


def get_available_provider_types() -> list:
    """
    获取可用 Provider 类型的便捷函数

    Returns:
        list: 支持的类型列表
    """
    return LLMProviderFactory.get_available_types()


def is_provider_type_supported(provider_type: str) -> bool:
    """
    检查 Provider 类型是否支持的便捷函数

    Args:
        provider_type: Provider 类型

    Returns:
        bool: True 如果支持
    """
    return LLMProviderFactory.is_type_supported(provider_type)
