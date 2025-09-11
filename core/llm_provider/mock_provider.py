"""
Mock Provider 实现
用于测试和开发的简单本地模拟
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional

from .base import LLMProvider, LLMConfig, LLMResponse

logger = logging.getLogger(__name__)


class MockProvider(LLMProvider):
    """
    Mock Provider

    简单的本地模拟，用于测试和开发，不需要外部依赖
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        # 预定义的模拟响应
        self._mock_responses = [
            "这是一个模拟的 AI 响应，用于测试目的。",
            "我明白了你的需求。让我帮你分析一下这个问题。",
            "根据你的描述，我建议采取以下步骤来解决这个问题。",
            "这是一个很有趣的问题。让我从几个角度来分析。",
            "好的，我来帮你制定一个详细的计划。",
            "这是一个常见的场景，我有几种解决方案可以推荐。",
            "让我先了解一下具体的需求和约束条件。",
            "这是一个很好的问题，我来给出一个全面的回答。",
        ]

        # 设置默认模型
        self._model = self.config.model_name or "mock-model-v1"

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        生成模拟响应

        Args:
            messages: 消息列表
            **kwargs: 额外参数（会被忽略）

        Returns:
            LLMResponse: 模拟的响应
        """
        start_time = time.time()

        try:
            # 模拟处理时间
            processing_time = random.uniform(0.1, 1.0)
            time.sleep(processing_time)

            # 选择随机响应
            content = random.choice(self._mock_responses)

            # 基于输入消息调整响应
            last_message = messages[-1] if messages else {}
            user_content = last_message.get("content", "")

            if "hello" in user_content.lower() or "hi" in user_content.lower():
                content = "你好！我是 TeamDev 的 AI 助手，很高兴为你服务。"
            elif "help" in user_content.lower():
                content = "我可以帮你进行项目管理、代码生成、文档编写等工作。请告诉我你需要什么帮助。"
            elif "project" in user_content.lower():
                content = "我可以帮你创建和管理项目，包括需求分析、架构设计、代码生成等。"
            elif len(user_content) > 100:
                content = "你提出了一个很详细的问题。让我仔细分析一下你的需求。"

            # 模拟 token 使用情况
            prompt_tokens = len(user_content) // 4  # 粗略估算
            completion_tokens = len(content) // 4

            llm_response = LLMResponse(
                content=content,
                model=self._model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                finish_reason="stop",
                response_time=time.time() - start_time
            )

            logger.debug(f"Mock 响应: {len(content)} 字符, 用时: {llm_response.response_time:.2f}s")
            return llm_response

        except Exception as e:
            error_msg = f"Mock Provider 模拟失败: {str(e)}"
            logger.error(error_msg)

            return LLMResponse(
                content="",
                model=self._model,
                response_time=time.time() - start_time,
                error=error_msg
            )

    def is_available(self) -> bool:
        """
        Mock Provider 总是可用的

        Returns:
            bool: 总是返回 True
        """
        return True

    def get_rate_limit_delay(self) -> float:
        """
        Mock Provider 没有速率限制

        Returns:
            float: 返回 0
        """
        return 0.0

    @property
    def model(self) -> str:
        """当前使用的模型名称"""
        return self._model

    def set_model(self, model_name: str):
        """
        设置使用的模型（Mock 不实际使用）

        Args:
            model_name: 模型名称
        """
        self._model = model_name
        logger.info(f"Mock Provider 切换模型到: {model_name}")

    def add_mock_response(self, response: str):
        """
        添加自定义的模拟响应

        Args:
            response: 要添加的响应文本
        """
        self._mock_responses.append(response)

    def set_mock_responses(self, responses: List[str]):
        """
        设置模拟响应列表

        Args:
            responses: 响应文本列表
        """
        self._mock_responses = responses.copy()

    def get_mock_responses(self) -> List[str]:
        """
        获取当前的模拟响应列表

        Returns:
            List[str]: 响应文本列表
        """
        return self._mock_responses.copy()
