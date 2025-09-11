"""
HTTP 请求工具
提供安全的 HTTP 请求功能
"""

import json
import logging
from typing import Dict, Any
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from permissions.permission_manager import check_permission

logger = logging.getLogger(__name__)


def _is_url_safe(url: str) -> bool:
    """
    检查 URL 是否安全

    Args:
        url: URL 字符串

    Returns:
        bool: True 如果 URL 安全，否则 False
    """
    try:
        parsed = urlparse(url)

        # 检查协议
        if parsed.scheme not in ['http', 'https']:
            return False

        # 检查是否是本地地址（防止 SSRF 攻击）
        hostname = parsed.hostname
        if not hostname:
            return False

        # 拒绝本地地址
        local_addresses = [
            'localhost', '127.0.0.1', '::1',
            '0.0.0.0', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'
        ]

        if hostname.lower() in local_addresses:
            return False

        # 检查是否是私有 IP
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except (ipaddress.AddressValueError, ValueError):
            # 不是 IP 地址，继续检查
            pass

        return True

    except Exception as e:
        logger.warning(f"URL 解析错误 {url}: {e}")
        return False


def _make_request_with_requests(url: str, method: str = 'GET',
                              headers: Dict[str, str] = None,
                              body: Any = None,
                              timeout: int = 30) -> Dict[str, Any]:
    """
    使用 requests 库发送 HTTP 请求

    Args:
        url: 请求 URL
        method: HTTP 方法
        headers: 请求头
        body: 请求体
        timeout: 超时时间

    Returns:
        Dict: 响应数据
    """
    response_data = {
        "status_code": 0,
        "headers": {},
        "body": "",
        "error": None
    }

    try:
        # 准备请求参数
        request_kwargs = {
            "url": url,
            "timeout": timeout
        }

        if headers:
            request_kwargs["headers"] = headers

        if body is not None:
            if isinstance(body, dict):
                request_kwargs["json"] = body
            else:
                request_kwargs["data"] = str(body)

        # 发送请求
        response = requests.request(method.upper(), **request_kwargs)

        response_data["status_code"] = response.status_code
        response_data["headers"] = dict(response.headers)

        # 处理响应体
        content_type = response.headers.get('content-type', '').lower()

        if 'application/json' in content_type:
            try:
                response_data["body"] = response.json()
            except:
                response_data["body"] = response.text
        else:
            response_data["body"] = response.text

    except requests.exceptions.Timeout:
        response_data["error"] = "请求超时"
    except requests.exceptions.ConnectionError:
        response_data["error"] = "连接错误"
    except requests.exceptions.RequestException as e:
        response_data["error"] = str(e)
    except Exception as e:
        response_data["error"] = f"未知错误: {str(e)}"

    return response_data


def _make_request_with_urllib(url: str, method: str = 'GET',
                             headers: Dict[str, str] = None,
                             body: Any = None,
                             timeout: int = 30) -> Dict[str, Any]:
    """
    使用 urllib 发送 HTTP 请求（requests 不可用时的后备方案）

    Args:
        url: 请求 URL
        method: HTTP 方法
        headers: 请求头
        body: 请求体
        timeout: 超时时间

    Returns:
        Dict: 响应数据
    """
    import urllib.request
    import urllib.error
    import socket

    response_data = {
        "status_code": 0,
        "headers": {},
        "body": "",
        "error": None
    }

    try:
        # 准备请求
        if body is not None:
            if isinstance(body, dict):
                data = json.dumps(body).encode('utf-8')
            else:
                data = str(body).encode('utf-8')
        else:
            data = None

        req = urllib.request.Request(url, data=data, method=method.upper())

        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        # 设置超时
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data["status_code"] = response.getcode() or 200
            response_data["headers"] = dict(response.headers)
            response_data["body"] = response.read().decode('utf-8', errors='ignore')

    except urllib.error.HTTPError as e:
        response_data["status_code"] = e.code
        response_data["body"] = e.read().decode('utf-8', errors='ignore')
    except (urllib.error.URLError, socket.timeout) as e:
        response_data["error"] = f"网络错误: {str(e)}"
    except Exception as e:
        response_data["error"] = f"未知错误: {str(e)}"

    return response_data


def run(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送 HTTP 请求

    Args:
        args: 包含以下字段的字典
            - url (str): 请求 URL，必填
            - method (str, 可选): HTTP 方法，默认为 "GET"
            - headers (dict, 可选): 请求头字典
            - body (str|dict, 可选): 请求体
            - timeout (int, 可选): 超时时间（秒），默认为 30
            - user_id (str): 用户ID，用于权限检查，必填

    Returns:
        Dict: 标准响应格式
            成功时: {"success": True, "output": {"status_code": 200, "headers": {...}, "body": "..."}}
            失败时: {"success": False, "error": {"error_code": "...", "message": "..."}}

    可能的错误码:
        - PERMISSION_DENIED: 用户没有 network:outbound 权限
        - INVALID_INPUT: 输入参数无效或 URL 不安全
        - NETWORK_ERROR: 网络请求失败
        - TIMEOUT: 请求超时
    """
    try:
        # 参数验证
        if not isinstance(args, dict):
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "输入参数必须是字典类型"
                }
            }

        # 提取必需参数
        url = args.get("url")
        user_id = args.get("user_id")

        if not url:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: url"
                }
            }

        if not user_id:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "缺少必需参数: user_id"
                }
            }

        # 权限检查
        if not check_permission(user_id, "network:outbound"):
            logger.warning(f"用户 {user_id} 尝试发送 HTTP 请求但没有权限: {url}")
            return {
                "success": False,
                "error": {
                    "error_code": "PERMISSION_DENIED",
                    "message": "用户没有网络访问权限"
                }
            }

        # URL 安全检查
        if not _is_url_safe(url):
            logger.warning(f"用户 {user_id} 尝试访问不安全 URL: {url}")
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": "URL 不安全或指向本地地址"
                }
            }

        # 获取可选参数
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        body = args.get("body")
        timeout = args.get("timeout", 30)

        # 验证方法
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method not in allowed_methods:
            return {
                "success": False,
                "error": {
                    "error_code": "INVALID_INPUT",
                    "message": f"不支持的 HTTP 方法: {method}"
                }
            }

        # 发送请求
        try:
            logger.info(f"用户 {user_id} 发送 HTTP 请求: {method} {url}")

            if REQUESTS_AVAILABLE:
                response_data = _make_request_with_requests(url, method, headers, body, timeout)
            else:
                response_data = _make_request_with_urllib(url, method, headers, body, timeout)

            if response_data["error"]:
                logger.error(f"HTTP 请求失败 {url}: {response_data['error']}")
                return {
                    "success": False,
                    "error": {
                        "error_code": "NETWORK_ERROR",
                        "message": response_data["error"]
                    }
                }

            logger.info(f"用户 {user_id} HTTP 请求成功: {method} {url} -> {response_data['status_code']}")
            return {
                "success": True,
                "output": {
                    "status_code": response_data["status_code"],
                    "headers": response_data["headers"],
                    "body": response_data["body"]
                }
            }

        except Exception as e:
            logger.error(f"发送 HTTP 请求时发生未知错误 {url}: {e}")
            return {
                "success": False,
                "error": {
                    "error_code": "NETWORK_ERROR",
                    "message": f"网络请求失败: {str(e)}"
                }
            }

    except Exception as e:
        logger.error(f"HTTP 请求工具执行时发生未捕获异常: {e}")
        return {
            "success": False,
            "error": {
                "error_code": "NETWORK_ERROR",
                "message": f"工具执行失败: {str(e)}"
            }
        }
