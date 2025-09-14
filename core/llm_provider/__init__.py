"""
LLM Provider 模块

本模块提供了统一的 AI 大语言模型调用接口，采用抽象工厂模式设计，
支持多种 LLM 服务提供商的无缝集成和切换。

模块架构：
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   应用层调用     │───▶│   工厂模式创建    │───▶│   具体Provider实现   │
│                │    │                  │    │                     │
│ create_provider │    │ LLMProviderFactory│    │ - OpenAIProvider    │
│ LLMConfig      │    │ PROVIDER_TYPES   │    │ - OllamaProvider    │
│ LLMResponse    │    │                  │    │ - MockProvider      │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                ▲                        ▲
                                │                        │
                         ┌──────────────┐        ┌─────────────┐
                         │   抽象基类    │        │   数据结构   │
                         │              │        │             │
                         │ LLMProvider  │        │ LLMConfig   │
                         │ (ABC)        │        │ LLMResponse │
                         └──────────────┘        └─────────────┘

核心组件：

1. 抽象层 (base.py)：
   - LLMProvider: 抽象基类，定义统一接口
   - LLMConfig: 配置数据结构
   - LLMResponse: 响应数据结构

2. 工厂层 (factory.py)：
   - LLMProviderFactory: 工厂类，负责实例创建
   - create_provider: 便捷创建函数
   - 类型注册和验证机制

3. 实现层：
   - OpenAIProvider: OpenAI GPT 系列模型支持
   - OllamaProvider: 本地 Ollama 模型支持  
   - MockProvider: 测试和开发用模拟实现

设计优势：
- 统一接口：所有 LLM 服务商使用相同的调用方式
- 配置驱动：通过配置文件灵活切换不同的服务商
- 易于扩展：添加新的 LLM 服务商只需实现抽象接口
- 类型安全：完善的类型提示和数据验证
- 测试友好：提供 Mock 实现，便于单元测试

快速开始：
    from core.llm_provider import create_provider, LLMConfig
    
    # 使用 OpenAI
    config = {
        "name": "gpt4",
        "type": "openai", 
        "api_key": "sk-...",
        "model_name": "gpt-4"
    }
    provider = create_provider(config)
    
    # 生成响应
    messages = [{"role": "user", "content": "Hello"}]
    response = provider.generate(messages)
    print(response.content)
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
from .lmstudio_provider import LMStudioProvider
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
    "LMStudioProvider",
    "MockProvider",
]
