"""
对比结果序列化器
"""
from rest_framework import serializers
from .models import ComparisonResult, AlertNotification


class ComparisonResultSerializer(serializers.ModelSerializer):
    """对比结果序列化器"""

    application_no = serializers.CharField(source='application.application_no', read_only=True)
    payment_no = serializers.CharField(source='payment.payment_no', read_only=True)
    severity = serializers.CharField(read_only=True)

    class Meta:
        model = ComparisonResult
        fields = '__all__'


class ComparisonDetailSerializer(serializers.ModelSerializer):
    """对比结果详情序列化器"""

    application = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    severity = serializers.CharField(read_only=True)

    class Meta:
        model = ComparisonResult
        fields = '__all__'

    def get_application(self, obj):
        """获取申请单信息"""
        app = obj.application
        return {
            'id': app.id,
            'application_no': app.application_no,
            'payee_name': app.payee_name,
            'payee_account': app.payee_account,
            'payee_bank': app.payee_bank,
            'amount': str(app.amount),
        }

    def get_payment(self, obj):
        """获取付款记录信息"""
        payment = obj.payment
        return {
            'id': payment.id,
            'payment_no': payment.payment_no,
            'actual_payee_name': payment.actual_payee_name,
            'actual_payee_account': payment.actual_payee_account,
            'actual_payee_bank': payment.actual_payee_bank,
            'actual_amount': str(payment.actual_amount),
        }


class VerifyComparisonSerializer(serializers.Serializer):
    """人工复核序列化器"""

    result = serializers.ChoiceField(choices=['normal', 'abnormal'])
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AlertNotificationSerializer(serializers.ModelSerializer):
    """差异预警通知序列化器"""

    comparison_id = serializers.IntegerField(source='comparison.id', read_only=True)
    application_no = serializers.CharField(
        source='comparison.application.application_no',
        read_only=True
    )

    class Meta:
        model = AlertNotification
        fields = '__all__'


class DifferenceListFilterSerializer(serializers.Serializer):
    """差异列表筛选序列化器"""

    severity = serializers.ChoiceField(
        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        required=False
    )
    verified = serializers.BooleanField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)