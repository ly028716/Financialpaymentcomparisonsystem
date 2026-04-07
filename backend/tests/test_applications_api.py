"""
付款申请 API 测试
测试目标：申请CRUD、状态流转、权限控制
"""
import pytest
from decimal import Decimal
from datetime import date


class TestApplicationCreateAPI:
    """创建申请API测试"""

    def test_create_application_success(self, api_client, create_user):
        """测试成功创建付款申请"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        data = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'payee_bank': '中国工商银行北京分行',
            'amount': '50000.00',
            'purpose': '服务器采购款',
        }

        response = api_client.post('/api/applications/', data, format='json')

        assert response.status_code == 201
        assert response.data['code'] == 201
        assert 'application_no' in response.data['data']

    def test_create_application_invalid_account(self, api_client, create_user):
        """测试创建申请时账号格式错误"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        data = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': 'invalid_account',  # 无效账号
            'payee_bank': '中国工商银行北京分行',
            'amount': '50000.00',
            'purpose': '服务器采购款',
        }

        response = api_client.post('/api/applications/', data, format='json')

        assert response.status_code == 400

    def test_create_application_missing_required_field(self, api_client, create_user):
        """测试创建申请时缺少必填字段"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        data = {
            'payee_name': '北京XX科技有限公司',
            # 缺少 payee_account
            'payee_bank': '中国工商银行北京分行',
            'amount': '50000.00',
        }

        response = api_client.post('/api/applications/', data, format='json')

        assert response.status_code == 400

    def test_create_application_unauthorized(self, api_client):
        """测试未登录创建申请"""
        data = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'amount': '50000.00',
        }

        response = api_client.post('/api/applications/', data, format='json')

        assert response.status_code == 401


class TestApplicationListAPI:
    """申请列表API测试"""

    def test_list_applications(self, api_client, create_user, create_application):
        """测试获取申请列表"""
        user = create_user(role='accountant')
        api_client.force_authenticate(user=user)

        # 创建测试数据
        create_application(payee_name='公司A')
        create_application(payee_name='公司B')

        response = api_client.get('/api/applications/')

        assert response.status_code == 200
        assert len(response.data['data']) >= 2

    def test_list_applications_filter_by_status(self, api_client, create_user, create_application):
        """测试按状态筛选申请列表"""
        user = create_user(role='accountant')
        api_client.force_authenticate(user=user)

        create_application(status='pending', payee_name='公司A')
        create_application(status='approved', payee_name='公司B')

        response = api_client.get('/api/applications/?status=pending')

        assert response.status_code == 200
        for item in response.data['data']:
            assert item['status'] == 'pending'

    def test_list_my_applications(self, api_client, create_user, create_application):
        """测试获取自己的申请列表"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        response = api_client.get('/api/applications/my/')

        assert response.status_code == 200


class TestApplicationDetailAPI:
    """申请详情API测试"""

    def test_get_application_detail(self, api_client, create_user, create_application):
        """测试获取申请详情"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        application = create_application()

        response = api_client.get(f'/api/applications/{application.id}/')

        assert response.status_code == 200
        assert response.data['data']['application_no'] == application.application_no

    def test_get_nonexistent_application(self, api_client, create_user):
        """测试获取不存在的申请"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        response = api_client.get('/api/applications/99999/')

        assert response.status_code == 404


class TestApplicationUpdateAPI:
    """申请更新API测试"""

    def test_update_draft_application(self, api_client, create_user, create_application):
        """测试更新草稿状态的申请"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        application = create_application(status='draft')

        data = {
            'payee_name': '新公司名称',
            'payee_account': application.payee_account,
            'payee_bank': application.payee_bank,
            'amount': str(application.amount),
            'purpose': application.purpose,
        }

        response = api_client.put(f'/api/applications/{application.id}/', data, format='json')

        assert response.status_code == 200

    def test_update_approved_application_forbidden(self, api_client, create_user, create_application):
        """测试更新已通过状态的申请（应被拒绝）"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        application = create_application(status='approved')

        data = {'payee_name': '新公司名称'}

        response = api_client.patch(f'/api/applications/{application.id}/', data, format='json')

        assert response.status_code == 403


class TestApplicationDeleteAPI:
    """申请撤销API测试"""

    def test_cancel_pending_application(self, api_client, create_user, create_application):
        """测试撤销待审核的申请"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        application = create_application(status='pending')

        response = api_client.delete(f'/api/applications/{application.id}/')

        assert response.status_code == 200

    def test_cancel_approved_application_forbidden(self, api_client, create_user, create_application):
        """测试撤销已通过的申请（应被拒绝）"""
        user = create_user(role='applicant')
        api_client.force_authenticate(user=user)

        application = create_application(status='approved')

        response = api_client.delete(f'/api/applications/{application.id}/')

        assert response.status_code == 403


class TestApproveRejectAPI:
    """审核通过/拒绝API测试"""

    def test_approve_application_by_accountant(self, api_client, create_user, create_application):
        """测试会计审核通过"""
        accountant = create_user(role='accountant')
        api_client.force_authenticate(user=accountant)

        application = create_application(status='pending', amount=Decimal('5000.00'))

        data = {'note': '信息完整，审核通过'}

        response = api_client.put(f'/api/applications/{application.id}/approve/', data, format='json')

        assert response.status_code == 200

    def test_approve_large_amount_by_accountant_forbidden(self, api_client, create_user, create_application):
        """测试会计审核大额付款（应被拒绝）"""
        accountant = create_user(role='accountant')
        api_client.force_authenticate(user=accountant)

        application = create_application(status='pending', amount=Decimal('100000.00'))

        data = {'note': '审核通过'}

        response = api_client.put(f'/api/applications/{application.id}/approve/', data, format='json')

        assert response.status_code == 403

    def test_approve_large_amount_by_finance_manager(self, api_client, create_user, create_application):
        """测试财务主管审核大额付款"""
        manager = create_user(role='finance_manager')
        api_client.force_authenticate(user=manager)

        application = create_application(status='pending', amount=Decimal('100000.00'))

        data = {'note': '审核通过'}

        response = api_client.put(f'/api/applications/{application.id}/approve/', data, format='json')

        assert response.status_code == 200

    def test_reject_application(self, api_client, create_user, create_application):
        """测试审核拒绝"""
        accountant = create_user(role='accountant')
        api_client.force_authenticate(user=accountant)

        application = create_application(status='pending')

        data = {'reason': '账号格式错误'}

        response = api_client.put(f'/api/applications/{application.id}/reject/', data, format='json')

        assert response.status_code == 200