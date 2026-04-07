"""
简化的权限测试 - 直接测试权限类逻辑
"""
import pytest
from django.contrib.auth import get_user_model
from payment_comparison.common.permissions import (
    IsApplicant, IsAccountant, IsCashier, IsFinanceManager, IsAdmin, Role
)

User = get_user_model()


class MockRequest:
    """模拟请求对象"""
    def __init__(self, user):
        self.user = user


@pytest.mark.django_db
class TestPermissionClasses:
    """测试权限类本身的逻辑"""

    def test_is_accountant_with_accountant_role(self):
        """测试IsAccountant权限类 - 会计角色应该通过"""
        user = User.objects.create_user(
            username='accountant_test',
            password='password',
            name='会计',
            email='accountant_test@test.com',
            department='财务部',
            role=Role.ACCOUNTANT
        )

        request = MockRequest(user)
        permission = IsAccountant()
        assert permission.has_permission(request, None) is True

    def test_is_accountant_with_admin_role(self):
        """测试IsAccountant权限类 - 管理员角色应该通过"""
        user = User.objects.create_user(
            username='admin_test',
            password='password',
            name='管理员',
            email='admin_test@test.com',
            department='管理部',
            role=Role.ADMIN
        )

        request = MockRequest(user)
        permission = IsAccountant()
        assert permission.has_permission(request, None) is True

    def test_is_accountant_with_cashier_role(self):
        """测试IsAccountant权限类 - 出纳角色应该被拒绝"""
        user = User.objects.create_user(
            username='cashier_test',
            password='password',
            name='出纳',
            email='cashier_test@test.com',
            department='财务部',
            role=Role.CASHIER
        )

        request = MockRequest(user)
        permission = IsAccountant()
        assert permission.has_permission(request, None) is False

    def test_is_cashier_with_cashier_role(self):
        """测试IsCashier权限类 - 出纳角色应该通过"""
        user = User.objects.create_user(
            username='cashier_test2',
            password='password',
            name='出纳',
            email='cashier_test2@test.com',
            department='财务部',
            role=Role.CASHIER
        )

        request = MockRequest(user)
        permission = IsCashier()
        assert permission.has_permission(request, None) is True

    def test_is_cashier_with_admin_role(self):
        """测试IsCashier权限类 - 管理员角色应该通过"""
        user = User.objects.create_user(
            username='admin_test2',
            password='password',
            name='管理员',
            email='admin_test2@test.com',
            department='管理部',
            role=Role.ADMIN
        )

        request = MockRequest(user)
        permission = IsCashier()
        assert permission.has_permission(request, None) is True

    def test_all_single_role_permissions_allow_admin(self):
        """测试所有单一角色权限类都允许管理员访问"""
        user = User.objects.create_user(
            username='admin_test3',
            password='password',
            name='管理员',
            email='admin_test3@test.com',
            department='管理部',
            role=Role.ADMIN
        )

        request = MockRequest(user)

        permission_classes = [
            IsApplicant(),
            IsAccountant(),
            IsCashier(),
            IsFinanceManager(),
            IsAdmin()
        ]

        for permission in permission_classes:
            result = permission.has_permission(request, None)
            assert result is True, \
                f"{permission.__class__.__name__} should allow admin, got {result}"

    def test_permission_isolation(self):
        """测试权限隔离 - 会计不能访问出纳接口"""
        accountant = User.objects.create_user(
            username='accountant_iso',
            password='password',
            name='会计',
            email='accountant_iso@test.com',
            department='财务部',
            role=Role.ACCOUNTANT
        )

        request = MockRequest(accountant)

        # 会计可以访问会计权限
        assert IsAccountant().has_permission(request, None) is True

        # 会计不能访问出纳权限
        assert IsCashier().has_permission(request, None) is False

        # 会计不能访问申请人权限
        assert IsApplicant().has_permission(request, None) is False
