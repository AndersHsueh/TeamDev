"""
LMStudio 本地模型 Provider 实现

本模块实现了 LMStudio 本地模型服务的集成，支持通过 LMStudio 的 OpenAI 兼容 API 调用本地部署的大语言模型。

核心功能：
- LMStudio API 集成：通过 OpenAI 兼容的 HTTP API 调用本地 LMStudio 服务
- 本地模型支持：支持所有 LMStudio 可运行的模型（Llama、Mistral、Qwen 等）
- 零配置启动：自动检测本地 LMStudio 服务状态
- 完全本地化：数据不出本地环境，保障隐私安全

适用场景：
- 私有化部署：完全本地运行，数据隐私安全
- 开发调试：便于本地开发和测试
- 离线使用：无需网络连接即可使用AI功能
- 模型管理：通过 LMStudio 图形界面管理模型

支持的模型：
- Llama 系列 (llama-2, llama-3, code-llama 等)
- Mistral 系列 (mistral-7b, mixtral-8x7b 等)
- Qwen 系列 (qwen-chat, qwen-coder 等)
- 其他 LMStudio 支持的 GGUF 格式模型

配置要求：
- base_url: LMStudio 服务地址 (默认: http://localhost:1234)
- model_name: 模型名称 (可选，由 LMStudio 自动管理)
- temperature: 温度参数 (0.0-2.0)
- max_tokens: 最大生成令牌数

依赖项：
- requests: HTTP 请求库
- LMStudio 应用: 需要本地安装并运行 LMStudio

使用示例：
    config = LLMConfig(
        name="lmstudio-local",
        type="lmstudio", 
        base_url="http://localhost:1234",
        temperature=0.7
    )
    provider = LMStudioProvider(config)
    response = provider.generate([{"role": "user", "content": "Hello"}])
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


class LMStudioProvider(LLMProvider):
    """
    LMStudio Provider

    通过 OpenAI 兼容的 HTTP API 调用本地部署的 LMStudio 模型
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package is not installed. Install with: pip install requests")

        # 默认 LMStudio API 地址
        self.base_url = self.config.base_url or "http://localhost:1234"
        
        # 确保 base_url 不以 / 结尾
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]

        # API 端点
        self.api_chat = f"{self.base_url}/v1/chat/completions"
        self.api_models = f"{self.base_url}/v1/models"

        # 设置默认模型（LMStudio 会自动使用当前加载的模型）
        self._model = self.config.model_name or "local-model"

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        调用 LMStudio API 生成响应

        Args:
            messages: 消息列表，格式如：
                [{"role": "user", "content": "Hello"}]
            **kwargs: 额外参数，会覆盖配置中的参数

        Returns:
            LLMResponse: 生成的响应
        """
        start_time = time.time()
        
        try:
            # 合并参数
            params = self._merge_params(**kwargs)
            
            # 构建请求数据
            request_data = {
                "model": self._model,
                "messages": messages,
                "temperature": params.get("temperature", 0.7),
                "stream": False  # 暂不支持流式响应
            }
            
            # 添加可选参数
            if params.get("max_tokens"):
                request_data["max_tokens"] = params["max_tokens"]
            
            if params.get("top_p"):
                request_data["top_p"] = params["top_p"]
                
            logger.debug(f"LMStudio API 请求: {request_data}")
            
            # 发送请求
            response = requests.post(
                self.api_chat,
                json=request_data,
                timeout=params.get("timeout", 60),
                headers={"Content-Type": "application/json"}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析响应
                content = ""
                usage = {}
                finish_reason = "stop"
                
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        content = choice["message"].get("content", "")
                    finish_reason = choice.get("finish_reason", "stop")
                
                if "usage" in result:
                    usage = {
                        "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                        "completion_tokens": result["usage"].get("completion_tokens", 0),
                        "total_tokens": result["usage"].get("total_tokens", 0)
                    }
                
                logger.info(f"LMStudio API 响应成功，用时 {response_time:.2f}s")
                
                return LLMResponse(
                    content=content,
                    model=self._model,
                    usage=usage,
                    finish_reason=finish_reason,
                    response_time=response_time
                )
            else:
                error_msg = f"LMStudio API 请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                return LLMResponse(
                    content="",
                    model=self._model,
                    error=error_msg,
                    response_time=response_time
                )
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"无法连接到 LMStudio 服务 ({self.base_url}): {e}"
            logger.error(error_msg)
            
            return LLMResponse(
                content="",
                model=self._model,
                error=error_msg,
                response_time=time.time() - start_time
            )
            
        except requests.exceptions.Timeout as e:
            error_msg = f"LMStudio API 请求超时: {e}"
            logger.error(error_msg)
            
            return LLMResponse(
                content="",
                model=self._model,
                error=error_msg,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            error_msg = f"LMStudio API 调用异常: {e}"
            logger.error(error_msg)
            
            return LLMResponse(
                content="",
                model=self._model,
                error=error_msg,
                response_time=time.time() - start_time
            )

    def is_available(self) -> bool:
        """
        检查 LMStudio 服务是否可用

        Returns:
            bool: True 如果服务可用，否则 False
        """
        try:
            response = requests.get(self.api_models, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                # 检查是否有可用的模型
                if "data" in models_data and len(models_data["data"]) > 0:
                    logger.info("LMStudio 服务可用，已加载模型")
                    return True
                else:
                    logger.warning("LMStudio 服务可用，但未加载任何模型")
                    return False
            else:
                logger.warning(f"LMStudio 服务响应异常: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"无法连接到 LMStudio 服务: {self.base_url}")
            return False
        except Exception as e:
            logger.warning(f"检查 LMStudio 服务可用性时出错: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        Returns:
            List[str]: 模型名称列表
        """
        try:
            response = requests.get(self.api_models, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                if "data" in models_data:
                    return [model.get("id", "unknown") for model in models_data["data"]]
            return []
        except Exception as e:
            logger.warning(f"获取模型列表失败: {e}")
            return []

    def get_rate_limit_delay(self) -> float:
        """
        获取请求间隔时间（用于限流）

        LMStudio 是本地服务，通常不需要限流

        Returns:
            float: 建议的延迟时间（秒）
        """
        return 0.0