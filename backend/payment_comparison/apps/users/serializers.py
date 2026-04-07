"""
用户序列化器
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'phone', 'department', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserBriefSerializer(serializers.ModelSerializer):
    """用户简要信息"""

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'department']