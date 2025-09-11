"""
测试 HTTP 请求工具
"""

import unittest
from unittest.mock import patch, MagicMock

from ..tools.http_request import run


class TestHttpRequest(unittest.TestCase):
    """测试 HttpRequest 工具"""

    def test_successful_get_request(self):
        """测试成功的 GET 请求"""
        args = {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "user_id": "admin"
        }

        # Mock requests response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"message": "success"}

        with patch('..tools.http_request.check_permission', return_value=True), \
             patch('..tools.http_request._make_request_with_requests', return_value={
                 "status_code": 200,
                 "headers": {"content-type": "application/json"},
                 "body": {"message": "success"},
                 "error": None
             }):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["status_code"], 200)
        self.assertEqual(result["output"]["body"], {"message": "success"})

    def test_post_request_with_body(self):
        """测试带请求体的 POST 请求"""
        args = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "body": {"key": "value"},
            "headers": {"content-type": "application/json"},
            "user_id": "admin"
        }

        with patch('..tools.http_request.check_permission', return_value=True), \
             patch('..tools.http_request._make_request_with_requests', return_value={
                 "status_code": 201,
                 "headers": {"content-type": "application/json"},
                 "body": {"received": {"key": "value"}},
                 "error": None
             }):

            result = run(args)

        self.assertTrue(result["success"])
        self.assertEqual(result["output"]["status_code"], 201)

    def test_unsafe_url(self):
        """测试不安全 URL 被拒绝"""
        args = {
            "url": "http://localhost:8080/internal",
            "user_id": "admin"
        }

        with patch('..tools.http_request.check_permission', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_network_error(self):
        """测试网络错误"""
        args = {
            "url": "https://nonexistent-domain-12345.com",
            "user_id": "admin"
        }

        with patch('..tools.http_request.check_permission', return_value=True), \
             patch('..tools.http_request._make_request_with_requests', return_value={
                 "status_code": 0,
                 "headers": {},
                 "body": "",
                 "error": "连接失败"
             }):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "NETWORK_ERROR")

    def test_permission_denied(self):
        """测试权限被拒绝"""
        args = {
            "url": "https://httpbin.org/get",
            "user_id": "user"
        }

        with patch('..tools.http_request.check_permission', return_value=False):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "PERMISSION_DENIED")

    def test_invalid_method(self):
        """测试无效的 HTTP 方法"""
        args = {
            "url": "https://httpbin.org/get",
            "method": "INVALID",
            "user_id": "admin"
        }

        with patch('..tools.http_request.check_permission', return_value=True):

            result = run(args)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

    def test_missing_required_args(self):
        """测试缺少必需参数"""
        # 缺少 url
        args = {"user_id": "admin"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")

        # 缺少 user_id
        args = {"url": "https://httpbin.org/get"}
        result = run(args)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["error_code"], "INVALID_INPUT")


if __name__ == '__main__':
    unittest.main()
