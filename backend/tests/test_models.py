"""
数据库 Model 测试
测试目标：付款申请表、实际付款记录表、对比结果表
"""
import pytest
from decimal import Decimal
from datetime import date


class TestPaymentApplicationModel:
    """付款申请 Model 测试"""

    def test_create_application(self):
        """测试创建付款申请"""
        from payment_comparison.apps.applications.models import PaymentApplication

        application = PaymentApplication(
            application_no='FK202604060001',
            department='技术部',
            applicant='张三',
            application_date=date(2026, 4, 6),
            payee_name='北京XX科技有限公司',
            payee_account='6222021234567890123',
            payee_bank='中国工商银行北京分行',
            amount=Decimal('50000.00'),
            purpose='服务器采购款',
            status='pending'
        )

        assert application.application_no == 'FK202604060001'
        assert application.department == '技术部'
        assert application.amount == Decimal('50000.00')
        assert application.status == 'pending'

    def test_application_status_choices(self):
        """测试申请状态选项"""
        from payment_comparison.apps.applications.models import PaymentApplication

        valid_statuses = ['draft', 'pending', 'approved', 'rejected', 'paid', 'verified']
        # 状态应该只能是这些值之一
        for status in valid_statuses:
            application = PaymentApplication(
                application_no='FK202604060001',
                status=status
            )
            assert application.status == status

    def test_application_amount_precision(self):
        """测试金额精度（保留2位小数）"""
        from payment_comparison.apps.applications.models import PaymentApplication

        application = PaymentApplication(
            application_no='FK202604060001',
            amount=Decimal('12345.67')
        )

        assert application.amount == Decimal('12345.67')

    def test_application_str(self):
        """测试字符串表示"""
        from payment_comparison.apps.applications.models import PaymentApplication

        application = PaymentApplication(
            application_no='FK202604060001',
            payee_name='测试公司'
        )

        assert 'FK202604060001' in str(application)


class TestActualPaymentModel:
    """实际付款记录 Model 测试"""

    def test_create_payment(self):
        """测试创建付款记录"""
        from payment_comparison.apps.payments.models import ActualPayment

        payment = ActualPayment(
            payment_no='PAY202604060001',
            application_id=1,
            actual_payee_name='北京XX科技有限公司',
            actual_payee_account='6222021234567890123',
            actual_amount=Decimal('50000.00'),
            payment_channel='网银转账',
            operator='李四'
        )

        assert payment.payment_no == 'PAY202604060001'
        assert payment.actual_amount == Decimal('50000.00')
        assert payment.payment_channel == '网银转账'

    def test_payment_voucher_json(self):
        """测试付款凭证JSON字段"""
        from payment_comparison.apps.payments.models import ActualPayment

        payment = ActualPayment(
            payment_no='PAY202604060001',
            payment_voucher=[
                {'file_id': 'f_001', 'file_name': '回单.jpg'}
            ]
        )

        assert len(payment.payment_voucher) == 1
        assert payment.payment_voucher[0]['file_id'] == 'f_001'


class TestComparisonResultModel:
    """对比结果 Model 测试"""

    def test_create_comparison_match(self):
        """测试创建匹配的对比结果"""
        from payment_comparison.apps.comparison.models import ComparisonResult

        result = ComparisonResult(
            application_id=1,
            payment_id=1,
            is_match=True,
            differences=[]
        )

        assert result.is_match is True
        assert result.differences == []

    def test_create_comparison_mismatch(self):
        """测试创建不匹配的对比结果"""
        from payment_comparison.apps.comparison.models import ComparisonResult

        result = ComparisonResult(
            application_id=1,
            payment_id=1,
            is_match=False,
            differences=[
                {
                    'field': '户名',
                    'expected': '北京XX科技有限公司',
                    'actual': '北京XX科技公司',
                    'severity': 'HIGH'
                }
            ]
        )

        assert result.is_match is False
        assert len(result.differences) == 1
        assert result.differences[0]['severity'] == 'HIGH'

    def test_comparison_verified(self):
        """测试对比结果复核"""
        from payment_comparison.apps.comparison.models import ComparisonResult

        result = ComparisonResult(
            application_id=1,
            payment_id=1,
            is_match=False,
            verified=True,
            verified_by='王主管'
        )

        assert result.verified is True
        assert result.verified_by == '王主管'


class TestUserModel:
    """用户 Model 测试"""

    def test_create_user(self):
        """测试创建用户"""
        from payment_comparison.apps.users.models import User

        user = User(
            username='zhangsan',
            name='张三',
            email='zhangsan@example.com',
            department='技术部',
            role='applicant'
        )

        assert user.username == 'zhangsan'
        assert user.role == 'applicant'
        assert user.department == '技术部'

    def test_user_role_choices(self):
        """测试用户角色选项"""
        from payment_comparison.apps.users.models import User

        valid_roles = ['applicant', 'accountant', 'cashier', 'finance_manager', 'admin']

        for role in valid_roles:
            user = User(username='test', role=role)
            assert user.role == role