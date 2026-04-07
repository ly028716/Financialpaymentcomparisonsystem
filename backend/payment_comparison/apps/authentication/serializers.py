"""
认证序列化器
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""

    username = serializers.CharField(
        label='用户名',
        required=True,
        error_messages={
            'required': '请输入用户名',
            'blank': '用户名不能为空'
        }
    )
    password = serializers.CharField(
        label='密码',
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': '请输入密码',
            'blank': '密码不能为空'
        }
    )
    captcha = serializers.CharField(
        label='验证码',
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError('用户名或密码错误')

        if not user.is_active:
            raise serializers.ValidationError('账户已被禁用')

        attrs['user'] = user
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """Token刷新序列化器"""

    refresh_token = serializers.CharField(
        label='刷新令牌',
        required=True
    )


class UserBriefSerializer(serializers.Serializer):
    """用户简要信息序列化器"""

    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField()
    department = serializers.CharField()