"""
实际付款序列化器
"""
from rest_framework import serializers
from decimal import Decimal
from datetime import datetime
from .models import ActualPayment


class ActualPaymentSerializer(serializers.ModelSerializer):
    """实际付款序列化器"""

    class Meta:
        model = ActualPayment
        fields = '__all__'
        read_only_fields = ['id', 'payment_no', 'created_at']

    def validate_actual_amount(self, value):
        """校验实际付款金额"""
        if value <= Decimal('0'):
            raise serializers.ValidationError('付款金额必须大于0')
        return value

    def validate_actual_payee_account(self, value):
        """校验实际收款账号"""
        from payment_comparison.apps.applications.utils import validate_bank_account

        result = validate_bank_account(value)
        if not result['valid']:
            raise serializers.ValidationError(result['message'])
        return value.replace(' ', '')

    def create(self, validated_data):
        """创建付款记录"""
        # 自动生成付款单号
        validated_data['payment_no'] = self._generate_payment_no()
        return super().create(validated_data)

    def _generate_payment_no(self):
        """生成付款单号"""
        from datetime import date
        today = date.today()
        prefix = f"PAY{today.strftime('%Y%m%d')}"

        last_payment = ActualPayment.objects.filter(
            payment_no__startswith=prefix
        ).order_by('-payment_no').first()

        if last_payment:
            last_no = int(last_payment.payment_no[-4:])
            new_no = last_no + 1
        else:
            new_no = 1

        return f"{prefix}{new_no:04d}"


class ActualPaymentListSerializer(serializers.ModelSerializer):
    """付款记录列表序列化器"""

    application_no = serializers.CharField(source='application.application_no', read_only=True)
    application_status = serializers.CharField(source='application.status', read_only=True)

    class Meta:
        model = ActualPayment
        fields = [
            'id', 'payment_no', 'application_id', 'application_no', 'application_status',
            'actual_payee_name', 'actual_amount', 'payment_channel',
            'operator', 'payment_date', 'created_at'
        ]


class PaymentWithComparisonSerializer(serializers.ModelSerializer):
    """带对比结果的付款序列化器"""

    comparison_result = serializers.SerializerMethodField()

    class Meta:
        model = ActualPayment
        fields = '__all__'

    def get_comparison_result(self, obj):
        """获取对比结果"""
        from payment_comparison.apps.comparison.models import ComparisonResult

        result = ComparisonResult.objects.filter(payment=obj).first()
        if result:
            return {
                'is_match': result.is_match,
                'differences': result.differences
            }
        return None


class BatchPaymentSerializer(serializers.Serializer):
    """批量付款序列化器"""

    payments = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )


class OCRResultSerializer(serializers.Serializer):
    """OCR识别结果序列化器"""

    payee_name = serializers.CharField(required=False, allow_blank=True)
    payee_account = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        required=False, allow_null=True
    )
    bank_serial_no = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False, allow_null=True)
    confidence = serializers.FloatField(required=False)
    raw_text = serializers.CharField(required=False, allow_blank=True)