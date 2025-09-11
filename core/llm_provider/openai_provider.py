"""
OpenAI API Provider 实现
支持 GPT 系列模型
"""

import time
import logging
from typing import Dict, List, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from .base import LLMProvider, LLMConfig, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI API Provider

    支持通过 OpenAI API 调用 GPT 系列模型
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is not installed. Install with: pip install openai")

        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )

        # 设置默认模型
        self._model = self.config.model_name or "gpt-3.5-turbo"

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        调用 OpenAI API 生成响应

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            LLMResponse: 生成的响应
        """
        start_time = time.time()

        try:
            # 合并参数
            params = self._merge_params(**kwargs)

            # 准备请求参数
            request_params = {
                "model": self._model,
                "messages": messages,
                "temperature": params.get("temperature", 0.7),
                "timeout": params.get("timeout", 30),
            }

            # 添加可选参数
            if "max_tokens" in params and params["max_tokens"]:
                request_params["max_tokens"] = params["max_tokens"]

            # 添加其他 OpenAI 特定参数
            for key in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
                if key in params and params[key] is not None:
                    request_params[key] = params[key]

            logger.debug(f"OpenAI 请求: {self._model}, 消息数: {len(messages)}")

            # 发送请求
            self._record_request_time()
            response = self.client.chat.completions.create(**request_params)

            # 解析响应
            choice = response.choices[0]
            content = choice.message.content or ""

            llm_response = LLMResponse(
                content=content,
                model=self._model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else {},
                finish_reason=choice.finish_reason,
                response_time=time.time() - start_time
            )

            logger.debug(f"OpenAI 响应: {len(content)} 字符, 用时: {llm_response.response_time:.2f}s")
            return llm_response

        except Exception as e:
            error_msg = f"OpenAI API 调用失败: {str(e)}"
            logger.error(error_msg)

            return LLMResponse(
                content="",
                model=self._model,
                response_time=time.time() - start_time,
                error=error_msg
            )

    def is_available(self) -> bool:
        """
        检查 OpenAI API 是否可用

        Returns:
            bool: True 如果可用
        """
        try:
            # 发送一个简单的测试请求
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.generate(test_messages, max_tokens=5)
            return response.error is None
        except Exception as e:
            logger.warning(f"OpenAI 可用性检查失败: {e}")
            return False

    def get_rate_limit_delay(self) -> float:
        """
        获取请求间隔时间

        OpenAI API 有速率限制，这里返回建议的延迟时间

        Returns:
            float: 建议的延迟时间（秒）
        """
        # GPT-3.5-turbo: 每分钟 200 个请求
        # GPT-4: 每分钟 50 个请求

        if "gpt-4" in self._model.lower():
            return 1.2  # 约每分钟 50 个请求
        else:
            return 0.3  # 约每分钟 200 个请求

    @property
    def model(self) -> str:
        """当前使用的模型名称"""
        return self._model

    def set_model(self, model_name: str):
        """
        设置使用的模型

        Args:
            model_name: 模型名称，如 "gpt-4", "gpt-3.5-turbo"
        """
        self._model = model_name
        logger.info(f"OpenAI Provider 切换模型到: {model_name}")
