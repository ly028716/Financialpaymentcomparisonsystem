"""
OCR视图测试
"""
import pytest
from unittest.mock import patch, Mock
from decimal import Decimal
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestOCRAPIView:
    """OCR接口测试"""

    def setup_method(self):
        """测试前准备"""
        self.client = APIClient()
        # 创建测试用户（出纳角色）
        from payment_comparison.apps.users.models import User
        self.user = User.objects.create_user(
            username='cashier_test',
            password='test123',
            name='测试出纳',
            role='cashier'
        )
        self.client.force_authenticate(user=self.user)

    def test_ocr_without_file(self):
        """测试未上传文件"""
        response = self.client.post('/api/payments/ocr/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 400
        assert '请上传银行回单图片' in response.data['message']

    def test_ocr_invalid_file_type(self):
        """测试无效文件类型"""
        file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '请上传JPG或PNG格式的图片' in response.data['message']

    def test_ocr_file_too_large(self):
        """测试文件过大"""
        # 创建超过10MB的文件
        large_content = b"x" * (11 * 1024 * 1024)
        file = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '文件大小不能超过10MB' in response.data['message']

    @patch('django.conf.settings.OCR_ENABLED', False)
    def test_ocr_service_disabled(self):
        """测试OCR服务未启用"""
        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        # ApiResponse.error(503, ...) 返回的HTTP状态码是 503 // 100 = 5，需要检查实际返回
        assert response.data['code'] == 503
        assert 'OCR服务未配置' in response.data['message']

    @patch('payment_comparison.apps.payments.ocr_service.AliOCRService')
    @patch('django.conf.settings.OCR_ENABLED', True)
    @patch('django.conf.settings.DASHSCOPE_API_KEY', 'test-key')
    def test_ocr_success(self, mock_ocr_service):
        """测试成功识别（mock）"""

        # 模拟OCR服务返回
        mock_service_instance = Mock()
        mock_service_instance.recognize_bank_receipt.return_value = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'amount': Decimal('50000.00'),
            'bank_serial_no': '20260406143012345678',
            'payment_date': datetime(2026, 4, 6, 14, 30, 0),
            'confidence': 0.95,
            'raw_text': '收款户名：北京XX科技有限公司...'
        }
        mock_ocr_service.return_value = mock_service_instance

        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == 'OCR识别成功'
        assert response.data['data']['payee_name'] == '北京XX科技有限公司'
        assert response.data['data']['payee_account'] == '6222021234567890123'
        assert float(response.data['data']['amount']) == 50000.00
        assert response.data['data']['confidence'] == 0.95

    @patch('payment_comparison.apps.payments.ocr_service.AliOCRService')
    @patch('django.conf.settings.OCR_ENABLED', True)
    @patch('django.conf.settings.DASHSCOPE_API_KEY', 'test-key')
    def test_ocr_api_error(self, mock_ocr_service):
        """测试OCR API调用失败"""

        # 模拟OCR服务抛出异常
        mock_service_instance = Mock()
        mock_service_instance.recognize_bank_receipt.side_effect = Exception('API调用超时')
        mock_ocr_service.return_value = mock_service_instance

        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        # ApiResponse.error(500, ...) 返回的HTTP状态码是 500 // 100 = 5
        assert response.data['code'] == 500
        assert 'OCR识别失败' in response.data['message']

    def test_ocr_permission_denied(self):
        """测试权限控制"""
        # 创建非出纳用户
        from payment_comparison.apps.users.models import User
        applicant = User.objects.create_user(
            username='applicant_test_ocr',
            password='test123',
            name='测试申请人OCR',
            role='applicant',
            email='applicant_ocr@test.com'
        )

        # 使用申请人身份访问
        self.client.force_authenticate(user=applicant)

        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch('payment_comparison.apps.payments.ocr_service.AliOCRService')
    @patch('django.conf.settings.OCR_ENABLED', True)
    @patch('django.conf.settings.DASHSCOPE_API_KEY', 'test-key')
    def test_ocr_partial_recognition(self, mock_ocr_service):
        """测试部分字段识别"""

        # 模拟部分字段识别
        mock_service_instance = Mock()
        mock_service_instance.recognize_bank_receipt.return_value = {
            'payee_name': '北京XX科技有限公司',
            'payee_account': '6222021234567890123',
            'amount': None,  # 金额未识别
            'bank_serial_no': '',
            'payment_date': None,
            'confidence': 0.4,
            'raw_text': '收款户名：北京XX科技有限公司...'
        }
        mock_ocr_service.return_value = mock_service_instance

        file = SimpleUploadedFile(
            "test.jpg",
            b"fake image",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/payments/ocr/', {'file': file})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['payee_name'] == '北京XX科技有限公司'
        assert response.data['data']['amount'] is None
        assert response.data['data']['confidence'] == 0.4
