"""
阿里云OCR服务封装
使用通义千问视觉API识别银行回单
"""
import base64
import re
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AliOCRService:
    """阿里云OCR服务封装"""

    def __init__(self, api_key: str):
        """
        初始化OCR服务

        Args:
            api_key: 阿里云DashScope API密钥
        """
        if not api_key:
            raise ValueError('DASHSCOPE_API_KEY不能为空')

        self.api_key = api_key

    def recognize_bank_receipt(self, image_file) -> Dict:
        """
        识别银行回单

        Args:
            image_file: Django UploadedFile对象

        Returns:
            {
                'payee_name': str,
                'payee_account': str,
                'amount': Decimal,
                'bank_serial_no': str,
                'payment_date': datetime,
                'confidence': float,
                'raw_text': str
            }
        """
        try:
            # 读取图片并转换为base64
            image_base64 = self._encode_image(image_file)

            # 调用通义千问视觉API
            api_response = self._call_dashscope_api(image_base64)

            # 解析API响应
            result = self._parse_ocr_result(api_response)

            return result

        except Exception as e:
            logger.error(f'OCR识别失败: {str(e)}', exc_info=True)
            raise

    def _encode_image(self, image_file) -> str:
        """
        将图片编码为base64

        Args:
            image_file: Django UploadedFile对象

        Returns:
            base64编码的图片字符串
        """
        image_file.seek(0)
        image_data = image_file.read()
        return base64.b64encode(image_data).decode('utf-8')

    def _call_dashscope_api(self, image_base64: str) -> Dict:
        """
        调用通义千问视觉API

        Args:
            image_base64: base64编码的图片

        Returns:
            API响应字典
        """
        try:
            from dashscope import MultiModalConversation

            messages = [
                {
                    'role': 'user',
                    'content': [
                        {
                            'image': f'data:image/jpeg;base64,{image_base64}'
                        },
                        {
                            'text': '''请识别这张银行回单/付款凭证，提取以下信息：
1. 收款户名（收款人名称）
2. 收款账号（银行卡号）
3. 付款金额
4. 银行流水号（交易流水号）
5. 付款日期

请按照以下格式输出：
收款户名：XXX
收款账号：XXX
付款金额：XXX
银行流水号：XXX
付款日期：YYYY-MM-DD

如果某个字段无法识别，请输出"未识别"。'''
                        }
                    ]
                }
            ]

            response = MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=messages,
                api_key=self.api_key
            )

            if response.status_code == 200:
                return response
            else:
                raise Exception(f'API调用失败: {response.code} - {response.message}')

        except ImportError:
            raise Exception('dashscope库未安装，请运行: pip install dashscope')
        except Exception as e:
            logger.error(f'调用DashScope API失败: {str(e)}')
            raise

    def _parse_ocr_result(self, api_response: Dict) -> Dict:
        """
        解析API响应，提取结构化数据

        Args:
            api_response: DashScope API响应

        Returns:
            结构化的OCR结果
        """
        try:
            # 提取识别文本
            output = api_response.output
            choices = output.get('choices', [])

            if not choices:
                raise Exception('API响应中没有识别结果')

            message = choices[0].get('message', {})
            content = message.get('content', [])

            # 提取文本内容
            raw_text = ''
            for item in content:
                if isinstance(item, dict) and item.get('text'):
                    raw_text += item['text']

            if not raw_text:
                raise Exception('未能提取到识别文本')

            # 从文本中提取字段
            fields = self._extract_fields(raw_text)

            # 计算置信度
            confidence = self._calculate_confidence(fields)

            return {
                'payee_name': fields.get('payee_name', ''),
                'payee_account': fields.get('payee_account', ''),
                'amount': fields.get('amount'),
                'bank_serial_no': fields.get('bank_serial_no', ''),
                'payment_date': fields.get('payment_date'),
                'confidence': confidence,
                'raw_text': raw_text
            }

        except Exception as e:
            logger.error(f'解析OCR结果失败: {str(e)}')
            raise

    def _extract_fields(self, text: str) -> Dict:
        """
        从文本中提取字段

        Args:
            text: 识别的原始文本

        Returns:
            提取的字段字典
        """
        fields = {}

        # 提取收款户名
        payee_name_patterns = [
            r'收款[户人]名[:：]\s*([^\n]+)',
            r'收款[户人][:：]\s*([^\n]+)',
            r'户\s*名[:：]\s*([^\n]+)',
        ]
        for pattern in payee_name_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if name and name != '未识别':
                    fields['payee_name'] = name
                    break

        # 提取收款账号
        account_patterns = [
            r'收款账号[:：]\s*(\d[\d\s]{15,25})',
            r'账\s*号[:：]\s*(\d[\d\s]{15,25})',
            r'卡\s*号[:：]\s*(\d[\d\s]{15,25})',
            r'(\d{16,19})',  # 直接匹配16-19位数字
        ]
        for pattern in account_patterns:
            match = re.search(pattern, text)
            if match:
                account = match.group(1).replace(' ', '').strip()
                if account and account != '未识别':
                    fields['payee_account'] = account
                    break

        # 提取付款金额
        amount_patterns = [
            r'付款金额[:：]\s*¥?\s*([\d,]+\.?\d*)',
            r'金\s*额[:：]\s*¥?\s*([\d,]+\.?\d*)',
            r'¥\s*([\d,]+\.?\d+)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '').strip()
                if amount_str and amount_str != '未识别':
                    try:
                        fields['amount'] = Decimal(amount_str)
                        break
                    except:
                        pass

        # 提取银行流水号
        serial_patterns = [
            r'银行流水号[:：]\s*(\w+)',
            r'流水号[:：]\s*(\w+)',
            r'交易流水号[:：]\s*(\w+)',
        ]
        for pattern in serial_patterns:
            match = re.search(pattern, text)
            if match:
                serial = match.group(1).strip()
                if serial and serial != '未识别':
                    fields['bank_serial_no'] = serial
                    break

        # 提取付款日期
        date_patterns = [
            r'付款日期[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})',
            r'日\s*期[:：]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                if date_str and date_str != '未识别':
                    try:
                        # 标准化日期格式
                        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                        fields['payment_date'] = datetime.strptime(date_str, '%Y-%m-%d')
                        break
                    except:
                        pass

        return fields

    def _calculate_confidence(self, fields: Dict) -> float:
        """
        计算识别置信度

        Args:
            fields: 提取的字段

        Returns:
            置信度（0-1之间）
        """
        # 关键字段权重
        weights = {
            'payee_name': 0.25,
            'payee_account': 0.30,
            'amount': 0.30,
            'bank_serial_no': 0.10,
            'payment_date': 0.05,
        }

        confidence = 0.0
        for field, weight in weights.items():
            if fields.get(field):
                confidence += weight

        return round(confidence, 2)
