"""
LLM Provider 模块
提供统一的 AI 模型调用接口
"""

from .base import LLMProvider, LLMConfig, LLMResponse
from .factory import (
    LLMProviderFactory,
    create_provider,
    get_available_provider_types,
    is_provider_type_supported
)
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .mock_provider import MockProvider

__all__ = [
    # 基础类和数据结构
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",

    # 工厂函数
    "LLMProviderFactory",
    "create_provider",
    "get_available_provider_types",
    "is_provider_type_supported",

    # 具体实现
    "OpenAIProvider",
    "OllamaProvider",
    "MockProvider",
]
