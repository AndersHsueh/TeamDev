"""
TeamDev 核心系统
提供 AI 模型调用和角色管理功能
"""

from .llm_provider import *
from .roles import *

__version__ = "0.1.0"

__all__ = [
    # LLM Provider 相关
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "create_provider",
    "OpenAIProvider",
    "OllamaProvider",
    "MockProvider",

    # 角色系统相关
    "Role",
    "RoleContext",
    "RoleAction",
    "Monica",
    "Jacky",
    "Happen",
    "Fei",
    "Peipei"
]
