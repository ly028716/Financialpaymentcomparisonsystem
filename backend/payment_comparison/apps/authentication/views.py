"""
认证视图
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from payment_comparison.common.response import ApiResponse
from .serializers import LoginSerializer, UserBriefSerializer

User = get_user_model()


class LoginView(APIView):
    """用户登录"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return ApiResponse.error(
                code=400,
                message='参数错误',
                data=serializer.errors
            )

        user = serializer.validated_data['user']

        # 生成Token
        refresh = RefreshToken.for_user(user)

        return ApiResponse.success(
            data={
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserBriefSerializer(user).data
            },
            message='登录成功'
        )


class LogoutView(APIView):
    """用户登出"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return ApiResponse.success(message='登出成功')
        except Exception as e:
            return ApiResponse.success(message='登出成功')


class TokenRefreshView(APIView):
    """Token刷新"""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return ApiResponse.error(code=400, message='缺少刷新令牌')

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return ApiResponse.success(
                data={
                    'access_token': access_token,
                    'refresh_token': str(refresh)
                },
                message='Token刷新成功'
            )
        except Exception as e:
            return ApiResponse.error(code=401, message='无效的刷新令牌')


class CurrentUserView(APIView):
    """获取当前用户信息"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return ApiResponse.success(
            data={
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'department': user.department,
                'role': user.role,
            }
        )


class ChangePasswordView(APIView):
    """修改密码"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return ApiResponse.error(code=400, message='请输入旧密码和新密码')

        if not user.check_password(old_password):
            return ApiResponse.error(code=400, message='旧密码错误')

        if len(new_password) < 6:
            return ApiResponse.error(code=400, message='新密码长度不能少于6位')

        user.set_password(new_password)
        user.save()

        return ApiResponse.success(message='密码修改成功')