"""
权限控制测试
测试目标：自定义权限类
"""
import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory


class TestRolePermissions:
    """角色权限测试类"""

    def test_is_applicant_permission(self):
        """测试部门申请人权限"""
        from payment_comparison.common.permissions import IsApplicant

        permission = IsApplicant()

        # 模拟请求
        request = Mock()
        request.user = Mock()
        request.user.role = 'applicant'

        assert permission.has_permission(request, None) is True

    def test_is_applicant_permission_denied(self):
        """测试非部门申请人被拒绝"""
        from payment_comparison.common.permissions import IsApplicant

        permission = IsApplicant()

        request = Mock()
        request.user = Mock()
        request.user.role = 'cashier'

        assert permission.has_permission(request, None) is False

    def test_is_accountant_permission(self):
        """测试会计权限"""
        from payment_comparison.common.permissions import IsAccountant

        permission = IsAccountant()

        request = Mock()
        request.user = Mock()
        request.user.role = 'accountant'

        assert permission.has_permission(request, None) is True

    def test_is_cashier_permission(self):
        """测试出纳权限"""
        from payment_comparison.common.permissions import IsCashier

        permission = IsCashier()

        request = Mock()
        request.user = Mock()
        request.user.role = 'cashier'

        assert permission.has_permission(request, None) is True

    def test_is_finance_manager_permission(self):
        """测试财务主管权限"""
        from payment_comparison.common.permissions import IsFinanceManager

        permission = IsFinanceManager()

        request = Mock()
        request.user = Mock()
        request.user.role = 'finance_manager'

        assert permission.has_permission(request, None) is True

    def test_is_admin_permission(self):
        """测试系统管理员权限"""
        from payment_comparison.common.permissions import IsAdmin

        permission = IsAdmin()

        request = Mock()
        request.user = Mock()
        request.user.role = 'admin'

        assert permission.has_permission(request, None) is True


class TestRoleHierarchy:
    """角色层级测试"""

    def test_admin_has_all_permissions(self):
        """测试管理员拥有所有权限"""
        from payment_comparison.common.permissions import IsAdmin

        permission = IsAdmin()
        request = Mock()
        request.user = Mock()
        request.user.role = 'admin'

        # 管理员应该能通过所有角色检查
        assert permission.has_permission(request, None) is True

    def test_finance_manager_can_approve_large_amount(self):
        """测试财务主管可以审批大额付款"""
        from payment_comparison.common.permissions import CanApproveLargeAmount

        permission = CanApproveLargeAmount()

        request = Mock()
        request.user = Mock()
        request.user.role = 'finance_manager'

        assert permission.has_permission(request, None) is True

    def test_accountant_cannot_approve_large_amount(self):
        """测试会计不能审批大额付款（≥10万）"""
        from payment_comparison.common.permissions import CanApproveLargeAmount

        permission = CanApproveLargeAmount()

        request = Mock()
        request.user = Mock()
        request.user.role = 'accountant'

        assert permission.has_permission(request, None) is False


class TestPermissionCombinations:
    """权限组合测试"""

    def test_accountant_or_finance_manager(self):
        """测试会计或财务主管权限"""
        from payment_comparison.common.permissions import IsAccountantOrFinanceManager

        permission = IsAccountantOrFinanceManager()

        # 会计
        request = Mock()
        request.user = Mock()
        request.user.role = 'accountant'
        assert permission.has_permission(request, None) is True

        # 财务主管
        request.user.role = 'finance_manager'
        assert permission.has_permission(request, None) is True

        # 出纳（无权限）
        request.user.role = 'cashier'
        assert permission.has_permission(request, None) is False

    def test_cashier_or_admin(self):
        """测试出纳或管理员权限"""
        from payment_comparison.common.permissions import IsCashierOrAdmin

        permission = IsCashierOrAdmin()

        # 出纳
        request = Mock()
        request.user = Mock()
        request.user.role = 'cashier'
        assert permission.has_permission(request, None) is True

        # 管理员
        request.user.role = 'admin'
        assert permission.has_permission(request, None) is True

        # 会计（无权限）
        request.user.role = 'accountant'
        assert permission.has_permission(request, None) is False