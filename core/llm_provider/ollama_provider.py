"""
Ollama 本地模型 Provider 实现
支持通过 Ollama API 调用本地部署的模型
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

from .base import LLMProvider, LLMConfig, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    Ollama Provider

    通过 HTTP API 调用本地部署的 Ollama 模型
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package is not installed. Install with: pip install requests")

        # 默认 Ollama API 地址
        self.base_url = self.config.base_url or "http://localhost:11434"

        # 设置默认模型
        self._model = self.config.model_name or "llama2"

        # API 端点
        self.api_generate = f"{self.base_url}/api/generate"
        self.api_tags = f"{self.base_url}/api/tags"

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        调用 Ollama API 生成响应

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

            # 将消息列表转换为 Ollama 格式
            prompt = self._convert_messages_to_prompt(messages)

            # 准备请求数据
            request_data = {
                "model": self._model,
                "prompt": prompt,
                "stream": False,  # 非流式响应
            }

            # 添加可选参数
            if "temperature" in params:
                request_data["temperature"] = params["temperature"]

            # Ollama 特定的参数
            ollama_params = ["top_p", "top_k", "num_predict", "stop"]
            for param in ollama_params:
                if param in params and params[param] is not None:
                    request_data[param] = params[param]

            logger.debug(f"Ollama 请求: {self._model}, 提示长度: {len(prompt)}")

            # 发送请求
            self._record_request_time()
            response = requests.post(
                self.api_generate,
                json=request_data,
                timeout=params.get("timeout", 30)
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API 返回错误状态码: {response.status_code}")

            result = response.json()

            # 解析响应
            content = result.get("response", "")
            usage = {}
            if "eval_count" in result:
                usage["completion_tokens"] = result["eval_count"]
            if "prompt_eval_count" in result:
                usage["prompt_tokens"] = result["prompt_eval_count"]

            llm_response = LLMResponse(
                content=content,
                model=self._model,
                usage=usage,
                finish_reason=result.get("done_reason"),
                response_time=time.time() - start_time
            )

            logger.debug(f"Ollama 响应: {len(content)} 字符, 用时: {llm_response.response_time:.2f}s")
            return llm_response

        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama 网络请求失败: {str(e)}"
            logger.error(error_msg)

            return LLMResponse(
                content="",
                model=self._model,
                response_time=time.time() - start_time,
                error=error_msg
            )

        except Exception as e:
            error_msg = f"Ollama 调用失败: {str(e)}"
            logger.error(error_msg)

            return LLMResponse(
                content="",
                model=self._model,
                response_time=time.time() - start_time,
                error=error_msg
            )

    def is_available(self) -> bool:
        """
        检查 Ollama 服务是否可用

        Returns:
            bool: True 如果可用
        """
        try:
            # 检查服务是否运行
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code != 200:
                return False

            # 检查模型是否存在
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]

            return self._model in model_names

        except Exception as e:
            logger.warning(f"Ollama 可用性检查失败: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        Returns:
            List[str]: 模型名称列表
        """
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception as e:
            logger.error(f"获取 Ollama 模型列表失败: {e}")
            return []

    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        将消息列表转换为 Ollama 格式的提示

        Args:
            messages: 消息列表

        Returns:
            str: 转换后的提示文本
        """
        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)

    def get_rate_limit_delay(self) -> float:
        """
        获取请求间隔时间

        Ollama 本地模型通常没有严格的速率限制

        Returns:
            float: 建议的延迟时间（秒）
        """
        return 0.1  # 较短的延迟，避免本地资源过载

    @property
    def model(self) -> str:
        """当前使用的模型名称"""
        return self._model

    def set_model(self, model_name: str):
        """
        设置使用的模型

        Args:
            model_name: 模型名称，如 "llama2", "codellama"
        """
        self._model = model_name
        logger.info(f"Ollama Provider 切换模型到: {model_name}")
