"""
权限修复验证测试

测试修复后的权限系统是否正常工作
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from payment_comparison.apps.applications.models import PaymentApplication
from payment_comparison.apps.payments.models import ActualPayment
from payment_comparison.common.permissions import (
    IsApplicant, IsAccountant, IsCashier, IsFinanceManager, IsAdmin,
    IsAccountantOrFinanceManager, IsCashierOrAdmin
)

User = get_user_model()


@pytest.fixture
def api_client():
    """API客户端"""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """管理员用户"""
    return User.objects.create_user(
        username='admin',
        password='admin123',
        name='管理员',
        email='admin@example.com',
        department='管理部',
        role='admin'
    )


@pytest.fixture
def accountant_user(db):
    """会计用户"""
    return User.objects.create_user(
        username='accountant',
        password='password',
        name='会计',
        email='accountant@example.com',
        department='财务部',
        role='accountant'
    )


@pytest.fixture
def cashier_user(db):
    """出纳用户"""
    return User.objects.create_user(
        username='cashier',
        password='password',
        name='出纳',
        email='cashier@example.com',
        department='财务部',
        role='cashier'
    )


@pytest.fixture
def applicant_user(db):
    """申请人用户"""
    return User.objects.create_user(
        username='applicant',
        password='password',
        name='申请人',
        email='applicant@example.com',
        department='技术部',
        role='applicant'
    )


@pytest.fixture
def finance_manager_user(db):
    """财务主管用户"""
    return User.objects.create_user(
        username='finance_manager',
        password='password',
        name='财务主管',
        email='manager@example.com',
        department='财务部',
        role='finance_manager'
    )


class TestPermissionClasses:
    """测试权限类本身的逻辑"""

    def test_is_accountant_with_accountant_role(self, accountant_user, db):
        """测试IsAccountant权限类 - 会计角色应该通过"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = accountant_user
        drf_request = Request(request)

        permission = IsAccountant()
        assert permission.has_permission(drf_request, None) is True

    def test_is_accountant_with_admin_role(self, admin_user, db):
        """测试IsAccountant权限类 - 管理员角色应该通过"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        drf_request = Request(request)

        permission = IsAccountant()
        assert permission.has_permission(drf_request, None) is True

    def test_is_accountant_with_cashier_role(self, cashier_user, db):
        """测试IsAccountant权限类 - 出纳角色应该被拒绝"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = cashier_user
        drf_request = Request(request)

        permission = IsAccountant()
        assert permission.has_permission(drf_request, None) is False

    def test_is_cashier_with_cashier_role(self, cashier_user, db):
        """测试IsCashier权限类 - 出纳角色应该通过"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = cashier_user
        drf_request = Request(request)

        permission = IsCashier()
        assert permission.has_permission(drf_request, None) is True

    def test_is_cashier_with_admin_role(self, admin_user, db):
        """测试IsCashier权限类 - 管理员角色应该通过"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        drf_request = Request(request)

        permission = IsCashier()
        assert permission.has_permission(drf_request, None) is True

    def test_all_single_role_permissions_allow_admin(self, admin_user, db):
        """测试所有单一角色权限类都允许管理员访问"""
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = admin_user
        drf_request = Request(request)

        permission_classes = [
            IsApplicant(),
            IsAccountant(),
            IsCashier(),
            IsFinanceManager(),
            IsAdmin()
        ]

        for permission in permission_classes:
            assert permission.has_permission(drf_request, None) is True, \
                f"{permission.__class__.__name__} should allow admin"


class TestAdminUserAccess:
    """测试管理员用户可以访问所有接口"""

    def test_admin_can_access_applications_list(self, api_client, admin_user):
        """管理员可以访问申请列表"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/applications/')
        assert response.status_code in [200, 404]  # 200成功或404无数据

    def test_admin_can_access_pending_applications(self, api_client, admin_user):
        """管理员可以访问待审核列表"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/applications/pending/')
        assert response.status_code in [200, 404]

    def test_admin_can_access_payments(self, api_client, admin_user):
        """管理员可以访问付款记录"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/payments/')
        assert response.status_code in [200, 404]

    def test_admin_can_access_comparison(self, api_client, admin_user):
        """管理员可以访问对比结果"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/comparison/')
        assert response.status_code in [200, 404]

    def test_admin_can_access_reports(self, api_client, admin_user):
        """管理员可以访问报表"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/reports/dashboard/')
        assert response.status_code == 200

    def test_admin_can_access_users(self, api_client, admin_user):
        """管理员可以访问用户管理"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 200


class TestAccountantUserAccess:
    """测试会计用户权限"""

    def test_accountant_can_access_pending_applications(self, api_client, accountant_user):
        """会计可以访问待审核列表"""
        api_client.force_authenticate(user=accountant_user)
        response = api_client.get('/api/applications/pending/')
        assert response.status_code in [200, 404]

    def test_accountant_can_access_comparison(self, api_client, accountant_user):
        """会计可以访问对比结果"""
        api_client.force_authenticate(user=accountant_user)
        response = api_client.get('/api/comparison/')
        assert response.status_code in [200, 404]

    def test_accountant_can_access_reports(self, api_client, accountant_user, db):
        """会计可以访问报表"""
        api_client.force_authenticate(user=accountant_user)
        response = api_client.get('/api/reports/dashboard/')
        assert response.status_code == 200

    def test_accountant_cannot_create_payment(self, api_client, accountant_user):
        """会计不能创建付款记录"""
        api_client.force_authenticate(user=accountant_user)
        response = api_client.post('/api/payments/', {})
        assert response.status_code == 403

    def test_accountant_cannot_access_users(self, api_client, accountant_user):
        """会计不能访问用户管理"""
        api_client.force_authenticate(user=accountant_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 403


class TestCashierUserAccess:
    """测试出纳用户权限"""

    def test_cashier_can_access_payments(self, api_client, cashier_user):
        """出纳可以访问付款记录"""
        api_client.force_authenticate(user=cashier_user)
        response = api_client.get('/api/payments/')
        assert response.status_code in [200, 404]

    def test_cashier_cannot_approve_application(self, api_client, cashier_user, db):
        """出纳不能审核申请"""
        api_client.force_authenticate(user=cashier_user)

        # 创建一个测试申请
        application = PaymentApplication.objects.create(
            application_no='FK202604060001',
            department='技术部',
            applicant='测试',
            application_date='2026-04-06',
            payee_name='测试公司',
            payee_account='6222021234567890123',
            payee_bank='工商银行',
            amount=10000.00,
            purpose='测试',
            status='pending'
        )

        response = api_client.put(f'/api/applications/{application.id}/approve/', {})
        assert response.status_code == 403

    def test_cashier_cannot_access_comparison(self, api_client, cashier_user):
        """出纳不能访问对比结果"""
        api_client.force_authenticate(user=cashier_user)
        response = api_client.get('/api/comparison/')
        assert response.status_code == 403

    def test_cashier_cannot_access_users(self, api_client, cashier_user):
        """出纳不能访问用户管理"""
        api_client.force_authenticate(user=cashier_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 403


class TestApplicantUserAccess:
    """测试申请人用户权限"""

    def test_applicant_can_access_own_applications(self, api_client, applicant_user):
        """申请人可以访问自己的申请"""
        api_client.force_authenticate(user=applicant_user)
        response = api_client.get('/api/applications/')
        assert response.status_code in [200, 404]

    def test_applicant_cannot_access_pending_applications(self, api_client, applicant_user):
        """申请人不能访问待审核列表（会计功能）"""
        api_client.force_authenticate(user=applicant_user)
        response = api_client.get('/api/applications/pending/')
        assert response.status_code == 403

    def test_applicant_cannot_create_payment(self, api_client, applicant_user):
        """申请人不能创建付款记录"""
        api_client.force_authenticate(user=applicant_user)
        response = api_client.post('/api/payments/', {})
        assert response.status_code == 403

    def test_applicant_cannot_access_comparison(self, api_client, applicant_user):
        """申请人不能访问对比结果"""
        api_client.force_authenticate(user=applicant_user)
        response = api_client.get('/api/comparison/')
        assert response.status_code == 403

    def test_applicant_cannot_access_users(self, api_client, applicant_user):
        """申请人不能访问用户管理"""
        api_client.force_authenticate(user=applicant_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 403


class TestUnauthenticatedAccess:
    """测试未登录用户访问"""

    def test_unauthenticated_cannot_access_applications(self, api_client):
        """未登录用户不能访问申请列表"""
        response = api_client.get('/api/applications/')
        assert response.status_code == 401

    def test_unauthenticated_cannot_access_payments(self, api_client):
        """未登录用户不能访问付款记录"""
        response = api_client.get('/api/payments/')
        assert response.status_code == 401

    def test_unauthenticated_cannot_access_comparison(self, api_client):
        """未登录用户不能访问对比结果"""
        response = api_client.get('/api/comparison/')
        assert response.status_code == 401

    def test_unauthenticated_cannot_access_users(self, api_client):
        """未登录用户不能访问用户管理"""
        response = api_client.get('/api/users/')
        assert response.status_code == 401


class TestUserManagementSecurity:
    """测试用户管理接口的安全性"""

    def test_only_admin_can_list_users(self, api_client, admin_user, accountant_user):
        """只有管理员可以查看用户列表"""
        # 管理员可以访问
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 200

        # 会计不能访问
        api_client.force_authenticate(user=accountant_user)
        response = api_client.get('/api/users/')
        assert response.status_code == 403

    def test_only_admin_can_create_user(self, api_client, admin_user, accountant_user):
        """只有管理员可以创建用户"""
        user_data = {
            'username': 'newuser',
            'password': 'password',
            'name': '新用户',
            'email': 'newuser@example.com',
            'department': '测试部',
            'role': 'applicant'
        }

        # 管理员可以创建
        api_client.force_authenticate(user=admin_user)
        response = api_client.post('/api/users/', user_data)
        assert response.status_code in [200, 201]

        # 会计不能创建
        api_client.force_authenticate(user=accountant_user)
        response = api_client.post('/api/users/', user_data)
        assert response.status_code == 403

    def test_only_admin_can_update_user(self, api_client, admin_user, accountant_user):
        """只有管理员可以更新用户"""
        # 管理员可以更新
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(f'/api/users/{accountant_user.id}/', {
            'name': '更新后的名字'
        })
        assert response.status_code in [200, 404]

        # 会计不能更新
        api_client.force_authenticate(user=accountant_user)
        response = api_client.patch(f'/api/users/{admin_user.id}/', {
            'name': '尝试更新管理员'
        })
        assert response.status_code == 403

    def test_only_admin_can_delete_user(self, api_client, admin_user, accountant_user, applicant_user):
        """只有管理员可以删除用户"""
        # 管理员可以删除
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f'/api/users/{applicant_user.id}/')
        assert response.status_code in [200, 204, 404]

        # 会计不能删除
        api_client.force_authenticate(user=accountant_user)
        response = api_client.delete(f'/api/users/{admin_user.id}/')
        assert response.status_code == 403


class TestPermissionConsistency:
    """测试权限一致性"""

    def test_permission_matrix_consistency(self, db):
        """测试权限矩阵与实际权限类的一致性"""
        from payment_comparison.common.permissions import PERMISSION_MATRIX, Role

        # 验证所有权限都包含ADMIN
        for permission_name, allowed_roles in PERMISSION_MATRIX.items():
            assert Role.ADMIN in allowed_roles, \
                f"Permission '{permission_name}' should include ADMIN role"

    def test_accountant_permission_includes_accountant_role(self, db):
        """测试IsAccountant权限类包含accountant角色"""
        from payment_comparison.common.permissions import Role
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request

        # 创建会计用户
        accountant = User.objects.create_user(
            username='test_accountant',
            password='password',
            name='测试会计',
            email='test@example.com',
            department='财务部',
            role=Role.ACCOUNTANT
        )

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = accountant
        drf_request = Request(request)

        permission = IsAccountant()
        assert permission.has_permission(drf_request, None) is True, \
            "IsAccountant should allow accountant role"
