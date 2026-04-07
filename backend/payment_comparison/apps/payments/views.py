"""
实际付款视图
"""
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal

from payment_comparison.common.response import ApiResponse
from payment_comparison.common.permissions import IsCashier, IsAdmin, IsCashierOrAdmin
from payment_comparison.apps.applications.models import PaymentApplication
from .models import ActualPayment
from .serializers import (
    ActualPaymentSerializer, ActualPaymentListSerializer,
    PaymentWithComparisonSerializer, BatchPaymentSerializer,
    OCRResultSerializer
)


class PaymentListAPIView(generics.ListCreateAPIView):
    """
    付款记录列表/创建

    GET: 获取付款记录列表
    POST: 创建付款记录（自动触发对比）
    """
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ActualPaymentSerializer
        return ActualPaymentListSerializer

    def get_queryset(self):
        queryset = ActualPayment.objects.all()

        # 筛选条件
        application_id = self.request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)

        operator = self.request.query_params.get('operator')
        if operator:
            queryset = queryset.filter(operator=operator)

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(payment_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__date__lte=end_date)

        return queryset.order_by('-payment_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error(400, '参数错误', serializer.errors)

        # 检查申请单是否存在且已审核
        application_id = request.data.get('application')
        try:
            application = PaymentApplication.objects.get(id=application_id)
        except PaymentApplication.DoesNotExist:
            return ApiResponse.error(404, '申请单不存在')

        if application.status != PaymentApplication.Status.APPROVED:
            return ApiResponse.error(400, '申请单未审核通过，无法付款')

        # 自动填充经办人
        serializer.save(operator=request.user.name)

        payment = serializer.instance

        # 更新申请单状态
        application.status = PaymentApplication.Status.PAID
        application.save()

        # 自动触发对比
        self._trigger_comparison(payment, application)

        # 重新获取对比结果
        payment.refresh_from_db()

        return ApiResponse.success(
            data={
                'id': payment.id,
                'payment_no': payment.payment_no,
                'application_id': payment.application_id,
                'status': application.status,
                'comparison_result': self._get_comparison_result(payment),
                'created_at': payment.created_at.isoformat()
            },
            message='付款记录成功'
        )

    def _trigger_comparison(self, payment, application):
        """触发对比"""
        from payment_comparison.apps.comparison.engine import compare_payment
        from payment_comparison.apps.comparison.models import ComparisonResult

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
        ComparisonResult.objects.create(
            application=application,
            payment=payment,
            is_match=result['is_match'],
            differences=result['differences']
        )

        # 如果有差异，创建预警通知
        if not result['is_match']:
            self._create_alert(payment, result)

    def _create_alert(self, payment, comparison_result):
        """创建差异预警"""
        from payment_comparison.apps.comparison.models import AlertNotification

        # 获取最高严重程度
        severity = 'LOW'
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        for diff in comparison_result.get('differences', []):
            diff_severity = diff.get('severity', 'LOW')
            if severity_order.index(diff_severity) < severity_order.index(severity):
                severity = diff_severity

        AlertNotification.objects.create(
            comparison_id=payment.comparison_results.first().id if payment.comparison_results.exists() else None,
            severity=severity,
            title=f'付款差异预警 - {payment.payment_no}',
            message=f'付款单 {payment.payment_no} 与申请单存在差异，请及时复核',
            recipients=['accountant', 'finance_manager'],
            status='pending'
        )

    def _get_comparison_result(self, payment):
        """获取对比结果"""
        from payment_comparison.apps.comparison.models import ComparisonResult

        result = ComparisonResult.objects.filter(payment=payment).first()
        if result:
            return {
                'is_match': result.is_match,
                'differences': result.differences
            }
        return None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return ApiResponse.paginated(
            data=serializer.data,
            total=queryset.count(),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20))
        )


class PaymentDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    付款记录详情

    GET: 获取付款详情
    PUT/PATCH: 更新付款信息
    """
    serializer_class = PaymentWithComparisonSerializer
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]
    queryset = ActualPayment.objects.all()


class PendingPaymentListView(generics.ListAPIView):
    """待付款列表"""
    serializer_class = ActualPaymentListSerializer
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]

    def get_queryset(self):
        # 获取已审核通过的申请单
        approved_applications = PaymentApplication.objects.filter(
            status=PaymentApplication.Status.APPROVED
        )

        # 获取已付款的申请单ID
        paid_application_ids = ActualPayment.objects.values_list(
            'application_id', flat=True
        )

        # 待付款 = 已审核 - 已付款
        pending_applications = approved_applications.exclude(
            id__in=paid_application_ids
        )

        return pending_applications


class BatchPaymentView(APIView):
    """批量付款"""
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]

    def post(self, request):
        serializer = BatchPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error(400, '参数错误', serializer.errors)

        payments_data = serializer.validated_data['payments']
        results = []
        success_count = 0
        failed_count = 0

        for payment_data in payments_data:
            application_id = payment_data.get('application_id')

            try:
                application = PaymentApplication.objects.get(id=application_id)
            except PaymentApplication.DoesNotExist:
                results.append({
                    'application_id': application_id,
                    'success': False,
                    'error': '申请单不存在'
                })
                failed_count += 1
                continue

            if application.status != PaymentApplication.Status.APPROVED:
                results.append({
                    'application_id': application_id,
                    'success': False,
                    'error': '申请单未审核通过'
                })
                failed_count += 1
                continue

            # 创建付款记录
            payment = ActualPayment.objects.create(
                application=application,
                payment_no=self._generate_payment_no(),
                actual_payee_name=payment_data.get('actual_payee_name', application.payee_name),
                actual_payee_account=payment_data.get('actual_payee_account', application.payee_account),
                actual_payee_bank=payment_data.get('actual_payee_bank', application.payee_bank),
                actual_amount=payment_data.get('actual_amount', application.amount),
                payment_channel=payment_data.get('payment_channel', 'online'),
                payment_voucher=payment_data.get('payment_voucher', []),
                operator=request.user.name,
                payment_date=timezone.now()
            )

            # 更新申请状态
            application.status = PaymentApplication.Status.PAID
            application.save()

            # 触发对比
            self._trigger_comparison(payment, application)

            results.append({
                'application_id': application_id,
                'payment_no': payment.payment_no,
                'is_match': not payment.comparison_results.exists() or
                           payment.comparison_results.first().is_match,
                'success': True
            })
            success_count += 1

        return ApiResponse.success(
            data={
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
            },
            message='批量付款记录完成'
        )

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

    def _trigger_comparison(self, payment, application):
        """触发对比"""
        from payment_comparison.apps.comparison.engine import compare_payment
        from payment_comparison.apps.comparison.models import ComparisonResult

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

        ComparisonResult.objects.create(
            application=application,
            payment=payment,
            is_match=result['is_match'],
            differences=result['differences']
        )


class OCRAPIView(APIView):
    """OCR识别银行回单"""
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]

    def post(self, request):
        from rest_framework.parsers import MultiPartParser, FormParser
        from django.conf import settings
        from .ocr_service import AliOCRService
        import logging

        logger = logging.getLogger(__name__)

        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return ApiResponse.error(400, '请上传银行回单图片')

        file = request.FILES['file']

        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            return ApiResponse.error(400, '请上传JPG或PNG格式的图片')

        # 检查文件大小（最大10MB）
        if file.size > 10 * 1024 * 1024:
            return ApiResponse.error(400, '文件大小不能超过10MB')

        # 检查OCR服务是否启用
        if not settings.OCR_ENABLED:
            return ApiResponse.error(
                503,
                'OCR服务未配置，请设置DASHSCOPE_API_KEY环境变量',
                {'fallback': '请手动录入付款信息'}
            )

        try:
            # 调用OCR服务
            ocr_service = AliOCRService(settings.DASHSCOPE_API_KEY)
            ocr_result = ocr_service.recognize_bank_receipt(file)

            # 序列化结果
            serializer = OCRResultSerializer(data=ocr_result)
            if serializer.is_valid():
                return ApiResponse.success(
                    data=serializer.data,
                    message='OCR识别成功'
                )
            else:
                logger.error(f'OCR结果序列化失败: {serializer.errors}')
                return ApiResponse.error(400, '识别结果格式错误', serializer.errors)

        except Exception as e:
            # 记录错误日志
            logger.error(f'OCR识别失败: {str(e)}', exc_info=True)

            return ApiResponse.error(
                500,
                f'OCR识别失败: {str(e)}',
                {'fallback': '请手动录入付款信息'}
            )