"""
统一响应格式模块
提供标准的 API 响应格式
"""
from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """
    统一 API 响应格式类

    响应格式：
    {
        "code": 200,           # 业务状态码
        "message": "success",  # 提示信息
        "data": {},            # 业务数据
        "meta": {}             # 分页元数据（可选）
    }
    """

    @staticmethod
    def success(data=None, message="success", meta=None):
        """
        成功响应

        Args:
            data: 业务数据（dict/list/None）
            message: 提示信息
            meta: 分页元数据（dict）

        Returns:
            Response: DRF Response 对象
        """
        response_data = {
            "code": 200,
            "message": message,
            "data": data
        }
        if meta is not None:
            response_data["meta"] = meta
        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def error(code, message, data=None):
        """
        错误响应

        Args:
            code: 错误码（400/401/403/404/500等）
            message: 错误信息
            data: 错误详情（可选）

        Returns:
            Response: DRF Response 对象
        """
        http_status = code // 100 if code >= 400 else status.HTTP_400_BAD_REQUEST
        if http_status < 400:
            http_status = status.HTTP_400_BAD_REQUEST

        response_data = {
            "code": code,
            "message": message,
            "data": data
        }
        return Response(response_data, status=http_status)

    @staticmethod
    def created(data=None, message="创建成功"):
        """创建成功响应（201）"""
        return Response({
            "code": 201,
            "message": message,
            "data": data
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def no_content(message="删除成功"):
        """无内容响应（204）"""
        return Response({
            "code": 204,
            "message": message,
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def paginated(data, total, page, page_size, message="success"):
        """
        分页响应

        Args:
            data: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页条数

        Returns:
            Response: DRF Response 对象
        """
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return ApiResponse.success(
            data=data,
            message=message,
            meta={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        )


# 错误码常量定义
class ErrorCodes:
    """错误码定义"""

    # 成功
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204

    # 客户端错误
    BAD_REQUEST = 400      # 参数错误
    UNAUTHORIZED = 401     # 未登录或Token失效
    FORBIDDEN = 403        # 无权限访问
    NOT_FOUND = 404        # 资源不存在
    CONFLICT = 409         # 资源冲突
    VALIDATION_ERROR = 422 # 业务校验失败
    RATE_LIMIT = 429       # 请求频率超限

    # 服务端错误
    INTERNAL_ERROR = 500   # 服务器内部错误
    SERVICE_UNAVAILABLE = 503  # 服务暂不可用