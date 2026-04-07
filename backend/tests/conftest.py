"""
Pytest 配置
"""
import sys
import os
import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_comparison.settings')

# 初始化 Django
import django
django.setup()


@pytest.fixture
def api_client():
    """API 客户端 fixture"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def create_user():
    """创建测试用户 fixture"""
    from payment_comparison.apps.users.models import User

    def _create_user(username='testuser', role='applicant', **kwargs):
        defaults = {
            'name': '测试用户',
            'email': f'{username}@test.com',
            'department': '测试部门',
            'role': role,
        }
        defaults.update(kwargs)
        user = User.objects.create_user(username=username, password='test123456', **defaults)
        return user

    return _create_user


@pytest.fixture
def create_application():
    """创建测试申请 fixture"""
    from payment_comparison.apps.applications.models import PaymentApplication
    from decimal import Decimal
    from datetime import date

    def _create_application(**kwargs):
        defaults = {
            'application_no': f'FK{date.today().strftime("%Y%m%d")}0001',
            'department': '技术部',
            'applicant': '张三',
            'application_date': date.today(),
            'payee_name': '测试收款方',
            'payee_account': '6222021234567890123',
            'payee_bank': '中国工商银行北京分行',
            'amount': Decimal('10000.00'),
            'purpose': '测试用途',
            'status': 'pending',
        }
        defaults.update(kwargs)
        application = PaymentApplication.objects.create(**defaults)
        return application

    return _create_application