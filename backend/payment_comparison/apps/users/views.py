"""
用户视图
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from payment_comparison.common.permissions import IsAdmin
from .models import User
from .serializers import UserSerializer


class UserListAPIView(generics.ListCreateAPIView):
    """
    用户列表/创建

    仅管理员可访问
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    用户详情/更新/删除

    仅管理员可访问
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]