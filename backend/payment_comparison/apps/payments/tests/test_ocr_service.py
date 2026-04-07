"""
OCR服务测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile


class TestAliOCRService:
    """阿里OCR服务测试"""

    def test_init_without_api_key(self):
        """测试无API密钥初始化"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        with pytest.raises(ValueError, match='DASHSCOPE_API_KEY不能为空'):
            AliOCRService('')

    def test_init_with_api_key(self):
        """测试有效API密钥初始化"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-api-key')
        assert service.api_key == 'test-api-key'

    @patch('dashscope.MultiModalConversation')
    def test_recognize_bank_receipt_success(self, mock_conversation):
        """测试成功识别银行回单"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.output = {
            'choices': [
                {
                    'message': {
                        'content': [
                            {
                                'text': '''收款户名：北京XX科技有限公司
收款账号：6222021234567890123
付款金额：50000.00
银行流水号：20260406143012345678
付款日期：2026-04-06'''
                            }
                        ]
                    }
                }
            ]
        }
        mock_conversation.call.return_value = mock_response

        # 创建测试图片
        image_file = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        # 执行识别
        service = AliOCRService('test-api-key')
        result = service.recognize_bank_receipt(image_file)

        # 验证结果
        assert result['payee_name'] == '北京XX科技有限公司'
        assert result['payee_account'] == '6222021234567890123'
        assert result['amount'] == Decimal('50000.00')
        assert result['bank_serial_no'] == '20260406143012345678'
        assert result['confidence'] > 0

    @patch('dashscope.MultiModalConversation')
    def test_recognize_bank_receipt_api_error(self, mock_conversation):
        """测试API调用失败"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        # 模拟API错误
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.code = 'InvalidParameter'
        mock_response.message = 'Invalid API key'
        mock_conversation.call.return_value = mock_response

        image_file = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        service = AliOCRService('invalid-key')

        with pytest.raises(Exception, match='API调用失败'):
            service.recognize_bank_receipt(image_file)

    def test_extract_fields_complete(self):
        """测试完整字段提取"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        text = '''收款户名：北京XX科技有限公司
收款账号：6222021234567890123
付款金额：¥50,000.00
银行流水号：20260406143012345678
付款日期：2026-04-06'''

        fields = service._extract_fields(text)

        assert fields['payee_name'] == '北京XX科技有限公司'
        assert fields['payee_account'] == '6222021234567890123'
        assert fields['amount'] == Decimal('50000.00')
        assert fields['bank_serial_no'] == '20260406143012345678'
        assert fields['payment_date'] is not None

    def test_extract_fields_partial(self):
        """测试部分字段提取"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        text = '''收款户名：北京XX科技有限公司
收款账号：6222021234567890123
付款金额：未识别'''

        fields = service._extract_fields(text)

        assert fields['payee_name'] == '北京XX科技有限公司'
        assert fields['payee_account'] == '6222021234567890123'
        assert fields.get('amount') is None

    def test_extract_account_with_spaces(self):
        """测试带空格的账号提取"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        text = '收款账号：6222 0212 3456 7890 123'
        fields = service._extract_fields(text)

        assert fields['payee_account'] == '6222021234567890123'

    def test_extract_amount_with_comma(self):
        """测试带千分位的金额提取"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        text = '付款金额：¥1,234,567.89'
        fields = service._extract_fields(text)

        assert fields['amount'] == Decimal('1234567.89')

    def test_calculate_confidence(self):
        """测试置信度计算"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        # 所有字段都有值
        fields_complete = {
            'payee_name': '测试公司',
            'payee_account': '1234567890',
            'amount': Decimal('1000'),
            'bank_serial_no': 'SN123',
            'payment_date': datetime.now()
        }
        confidence = service._calculate_confidence(fields_complete)
        assert confidence == 1.0

        # 部分字段有值
        fields_partial = {
            'payee_name': '测试公司',
            'payee_account': '1234567890',
            'amount': None,
            'bank_serial_no': '',
            'payment_date': None
        }
        confidence = service._calculate_confidence(fields_partial)
        assert 0 < confidence < 1.0

    def test_encode_image(self):
        """测试图片编码"""
        from payment_comparison.apps.payments.ocr_service import AliOCRService

        service = AliOCRService('test-key')

        image_file = SimpleUploadedFile(
            "test.jpg",
            b"test content",
            content_type="image/jpeg"
        )

        base64_str = service._encode_image(image_file)

        assert isinstance(base64_str, str)
        assert len(base64_str) > 0
