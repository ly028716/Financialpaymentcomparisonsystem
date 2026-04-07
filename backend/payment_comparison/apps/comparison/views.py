"""
对比结果视图
"""
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from payment_comparison.common.response import ApiResponse
from payment_comparison.common.permissions import IsFinanceManager, IsAdmin, IsAccountantOrFinanceManager
from .models import ComparisonResult, AlertNotification
from .serializers import (
    ComparisonResultSerializer, ComparisonDetailSerializer,
    VerifyComparisonSerializer, AlertNotificationSerializer,
    DifferenceListFilterSerializer
)


class ComparisonListAPIView(generics.ListCreateAPIView):
    """
    对比结果列表

    GET: 获取对比结果列表
    POST: 手动触发对比
    """
    serializer_class = ComparisonResultSerializer
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]
    queryset = ComparisonResult.objects.all()

    def get_queryset(self):
        queryset = ComparisonResult.objects.all()

        is_match = self.request.query_params.get('is_match')
        if is_match is not None:
            queryset = queryset.filter(is_match=is_match.lower() == 'true')

        verified = self.request.query_params.get('verified')
        if verified is not None:
            queryset = queryset.filter(verified=verified.lower() == 'true')

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return ApiResponse.paginated(
            data=serializer.data,
            total=queryset.count(),
            page=request.query_params.get('page', 1),
            page_size=request.query_params.get('page_size', 20)
        )


class ComparisonDetailAPIView(generics.RetrieveAPIView):
    """
    对比结果详情

    GET: 获取对比详情
    """
    serializer_class = ComparisonDetailSerializer
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]
    queryset = ComparisonResult.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)


class DifferenceListView(generics.ListAPIView):
    """差异列表（仅不匹配的结果）"""
    serializer_class = ComparisonDetailSerializer
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]

    def get_queryset(self):
        queryset = ComparisonResult.objects.filter(is_match=False)

        # 筛选严重程度
        severity = self.request.query_params.get('severity')
        if severity:
            # 使用JSON字段查询
            queryset = queryset.filter(
                differences__contains=[{'severity': severity}]
            )

        # 筛选复核状态
        verified = self.request.query_params.get('verified')
        if verified is not None:
            queryset = queryset.filter(verified=verified.lower() == 'true')

        # 筛选日期范围
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return ApiResponse.paginated(
            data=serializer.data,
            total=queryset.count(),
            page=request.query_params.get('page', 1),
            page_size=request.query_params.get('page_size', 20)
        )


class VerifyComparisonView(APIView):
    """人工复核"""
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def put(self, request, id):
        try:
            comparison = ComparisonResult.objects.get(id=id)
        except ComparisonResult.DoesNotExist:
            return ApiResponse.error(404, '对比结果不存在')

        if comparison.verified:
            return ApiResponse.error(400, '该对比结果已复核')

        serializer = VerifyComparisonSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error(400, '参数错误', serializer.errors)

        # 更新复核信息
        comparison.verified = True
        comparison.verified_by = request.user.name
        comparison.verified_at = timezone.now()
        comparison.verification_note = serializer.validated_data.get('note', '')
        comparison.save()

        # 更新申请单状态
        application = comparison.application
        if serializer.validated_data['result'] == 'normal':
            application.status = application.Status.VERIFIED
        application.save()

        return ApiResponse.success(
            data={
                'id': comparison.id,
                'verified': True,
                'verified_by': request.user.name,
                'verified_at': comparison.verified_at.isoformat(),
                'verification_note': comparison.verification_note
            },
            message='复核完成'
        )


class AlertNotificationListView(generics.ListAPIView):
    """预警通知列表"""
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]

    def get_queryset(self):
        queryset = AlertNotification.objects.all()

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset.order_by('-created_at')


class AlertNotificationReadView(APIView):
    """标记预警已读"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            notification = AlertNotification.objects.get(id=id)
        except AlertNotification.DoesNotExist:
            return ApiResponse.error(404, '通知不存在')

        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()

        return ApiResponse.success(message='已标记为已读')


class TriggerComparisonView(APIView):
    """手动触发对比"""
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]

    def post(self, request):
        from payment_comparison.apps.applications.models import PaymentApplication
        from payment_comparison.apps.payments.models import ActualPayment
        from .engine import compare_payment

        application_id = request.data.get('application_id')
        payment_id = request.data.get('payment_id')

        if not application_id or not payment_id:
            return ApiResponse.error(400, '请提供申请单ID和付款记录ID')

        try:
            application = PaymentApplication.objects.get(id=application_id)
            payment = ActualPayment.objects.get(id=payment_id)
        except (PaymentApplication.DoesNotExist, ActualPayment.DoesNotExist):
            return ApiResponse.error(404, '申请单或付款记录不存在')

        # 执行对比
        application_data = {
            'payee_name': application.payee_name,
            'payee_account': application.payee_account,
            'payee_bank': application.payee_bank,
            'amount': application.amount,
        }

        payment_data = {
            'actual_payee_name': payment.actual_payee_name,
            'actual_payee_account': payment.actual_payee_account,
            'actual_payee_bank': payment.actual_payee_bank,
            'actual_amount': payment.actual_amount,
        }

        result = compare_payment(application_data, payment_data)

        # 保存对比结果
        comparison = ComparisonResult.objects.create(
            application=application,
            payment=payment,
            is_match=result['is_match'],
            differences=result['differences']
        )

        return ApiResponse.success(
            data={
                'id': comparison.id,
                'is_match': comparison.is_match,
                'differences': comparison.differences
            },
            message='对比完成'
        )