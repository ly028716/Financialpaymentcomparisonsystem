"""
付款申请序列化器
"""
from rest_framework import serializers
from decimal import Decimal
from datetime import date
from .models import PaymentApplication, AuditLog
from .utils import validate_bank_account


class PaymentApplicationSerializer(serializers.ModelSerializer):
    """付款申请序列化器"""

    amount_cn = serializers.CharField(read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)

    class Meta:
        model = PaymentApplication
        fields = [
            'id', 'application_no', 'department', 'applicant', 'application_date',
            'payee_name', 'payee_account', 'payee_bank',
            'amount', 'amount_cn', 'purpose', 'attachments',
            'status', 'urgent', 'remark',
            'can_edit', 'can_delete',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'application_no', 'department', 'applicant', 'application_date',
            'status', 'created_at', 'updated_at'
        ]

    def validate_payee_account(self, value):
        """校验收款方账号"""
        result = validate_bank_account(value)
        if not result['valid']:
            raise serializers.ValidationError(result['message'])
        return value.replace(' ', '')

    def validate_amount(self, value):
        """校验付款金额"""
        if value <= Decimal('0'):
            raise serializers.ValidationError('付款金额必须大于0')
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError('付款金额超出上限')
        return value

    def validate_payee_name(self, value):
        """校验收款方户名"""
        if not value or not value.strip():
            raise serializers.ValidationError('收款方户名不能为空')
        # 检查特殊字符
        import re
        if re.search(r'[<>\"\'\\]', value):
            raise serializers.ValidationError('收款方户名包含非法字符')
        return value.strip()

    def create(self, validated_data):
        """创建付款申请"""
        request = self.context.get('request')
        user = request.user if request else None

        # 自动填充申请人信息
        if user:
            validated_data['applicant'] = user.name
            validated_data['department'] = user.department

        # 自动生成申请单号
        validated_data['application_no'] = self._generate_application_no()
        validated_data['application_date'] = date.today()
        validated_data['status'] = PaymentApplication.Status.PENDING

        return super().create(validated_data)

    def _generate_application_no(self):
        """生成申请单号"""
        today = date.today()
        prefix = f"FK{today.strftime('%Y%m%d')}"

        # 查询今天的最大流水号
        last_app = PaymentApplication.objects.filter(
            application_no__startswith=prefix
        ).order_by('-application_no').first()

        if last_app:
            last_no = int(last_app.application_no[-4:])
            new_no = last_no + 1
        else:
            new_no = 1

        return f"{prefix}{new_no:04d}"


class PaymentApplicationListSerializer(serializers.ModelSerializer):
    """付款申请列表序列化器（简化版）"""

    class Meta:
        model = PaymentApplication
        fields = [
            'id', 'application_no', 'department', 'applicant',
            'payee_name', 'payee_account', 'amount',
            'purpose', 'status', 'urgent', 'created_at'
        ]


class PaymentApplicationDetailSerializer(serializers.ModelSerializer):
    """付款申请详情序列化器"""

    amount_cn = serializers.CharField(read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)
    audit_history = serializers.SerializerMethodField()

    class Meta:
        model = PaymentApplication
        fields = '__all__'

    def get_audit_history(self, obj):
        """获取审核历史"""
        logs = obj.audit_logs.all()[:10]
        return AuditLogSerializer(logs, many=True).data


class AuditLogSerializer(serializers.ModelSerializer):
    """审核日志序列化器"""

    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['action', 'action_display', 'operator', 'note', 'created_at']


class ApproveApplicationSerializer(serializers.Serializer):
    """审核通过序列化器"""

    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class RejectApplicationSerializer(serializers.Serializer):
    """审核拒绝序列化器"""

    reason = serializers.CharField(required=True, max_length=500)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class BatchApproveSerializer(serializers.Serializer):
    """批量审核序列化器"""

    application_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)