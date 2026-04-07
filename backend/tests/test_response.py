"""
统一响应格式测试
测试目标：ApiResponse 类
"""
import pytest
from rest_framework.response import Response


class TestApiResponse:
    """统一响应格式测试类"""

    def test_success_response_basic(self):
        """测试基本成功响应"""
        # 这个测试会失败，因为 ApiResponse 类还不存在
        from common.response import ApiResponse

        response = ApiResponse.success(data={"id": 1}, message="success")

        assert response.status_code == 200
        assert response.data["code"] == 200
        assert response.data["message"] == "success"
        assert response.data["data"] == {"id": 1}

    def test_success_response_with_meta(self):
        """测试带分页元数据的成功响应"""
        from common.response import ApiResponse

        meta = {"total": 100, "page": 1, "page_size": 20}
        response = ApiResponse.success(
            data=[{"id": 1}, {"id": 2}],
            message="success",
            meta=meta
        )

        assert response.data["meta"] == meta
        assert response.data["data"] == [{"id": 1}, {"id": 2}]

    def test_error_response(self):
        """测试错误响应"""
        from common.response import ApiResponse

        response = ApiResponse.error(code=400, message="参数错误")

        assert response.status_code == 400
        assert response.data["code"] == 400
        assert response.data["message"] == "参数错误"

    def test_error_response_with_data(self):
        """测试带数据的错误响应"""
        from common.response import ApiResponse

        response = ApiResponse.error(
            code=422,
            message="业务校验失败",
            data={"field": "amount", "reason": "金额超出范围"}
        )

        assert response.data["data"] == {"field": "amount", "reason": "金额超出范围"}

    def test_success_with_null_data(self):
        """测试空数据的成功响应"""
        from common.response import ApiResponse

        response = ApiResponse.success(data=None, message="删除成功")

        assert response.data["data"] is None


class TestApiResponseStatusCodes:
    """响应状态码测试"""

    def test_400_bad_request(self):
        """测试400状态码"""
        from common.response import ApiResponse

        response = ApiResponse.error(400, "参数错误")
        assert response.status_code == 400

    def test_401_unauthorized(self):
        """测试401状态码"""
        from common.response import ApiResponse

        response = ApiResponse.error(401, "未登录")
        assert response.status_code == 401

    def test_403_forbidden(self):
        """测试403状态码"""
        from common.response import ApiResponse

        response = ApiResponse.error(403, "无权限")
        assert response.status_code == 403

    def test_404_not_found(self):
        """测试404状态码"""
        from common.response import ApiResponse

        response = ApiResponse.error(404, "资源不存在")
        assert response.status_code == 404

    def test_500_internal_error(self):
        """测试500状态码"""
        from common.response import ApiResponse

        response = ApiResponse.error(500, "服务器内部错误")
        assert response.status_code == 500