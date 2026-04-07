"""
报表统计视图
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta

from payment_comparison.common.response import ApiResponse
from payment_comparison.common.permissions import IsFinanceManager, IsAdmin, IsAccountantOrFinanceManager
from payment_comparison.apps.applications.models import PaymentApplication
from payment_comparison.apps.payments.models import ActualPayment
from payment_comparison.apps.comparison.models import ComparisonResult


class PaymentStatsView(APIView):
    """付款统计"""
    permission_classes = [IsAuthenticated, IsAccountantOrFinanceManager]

    def get(self, request):
        dimension = request.query_params.get('dimension', 'department')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')

        queryset = PaymentApplication.objects.filter(
            status__in=['approved', 'paid', 'verified']
        )

        if start_date:
            queryset = queryset.filter(application_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(application_date__lte=end_date)

        # 总计
        total_count = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0

        result = {
            'total_count': total_count,
            'total_amount': float(total_amount),
        }

        # 按维度统计
        if dimension == 'department':
            stats = queryset.values('department').annotate(
                count=Count('id'),
                amount=Sum('amount')
            ).order_by('-amount')

            result['by_department'] = [
                {
                    'department': item['department'],
                    'count': item['count'],
                    'amount': float(item['amount'] or 0),
                    'percentage': round(item['count'] / total_count * 100, 1) if total_count > 0 else 0
                }
                for item in stats
            ]

        elif dimension == 'status':
            stats = queryset.values('status').annotate(
                count=Count('id'),
                amount=Sum('amount')
            ).order_by('status')

            result['by_status'] = [
                {
                    'status': item['status'],
                    'count': item['count'],
                    'amount': float(item['amount'] or 0),
                }
                for item in stats
            ]

        elif dimension == 'time':
            if group_by == 'month':
                trunc = TruncMonth('application_date')
            else:
                trunc = TruncDate('application_date')

            stats = queryset.annotate(
                period=trunc
            ).values('period').annotate(
                count=Count('id'),
                amount=Sum('amount')
            ).order_by('period')

            result['by_time'] = [
                {
                    'date': item['period'].strftime('%Y-%m-%d'),
                    'count': item['count'],
                    'amount': float(item['amount'] or 0),
                }
                for item in stats
            ]

        return ApiResponse.success(data=result)


class DifferenceAnalysisView(APIView):
    """差异分析"""
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # 所有对比结果
        queryset = ComparisonResult.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        total_payments = queryset.count()
        difference_count = queryset.filter(is_match=False).count()

        result = {
            'total_payments': total_payments,
            'difference_count': difference_count,
            'difference_rate': round(difference_count / total_payments * 100, 1) if total_payments > 0 else 0,
        }

        # 按严重程度统计
        severity_stats = []
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = queryset.filter(
                differences__contains=[{'severity': severity}]
            ).count()
            severity_stats.append({
                'severity': severity,
                'count': count,
                'percentage': round(count / difference_count * 100, 1) if difference_count > 0 else 0
            })
        result['by_severity'] = severity_stats

        # 按差异字段统计
        field_stats = []
        for field in ['账号', '户名', '金额', '开户行']:
            count = queryset.filter(
                differences__contains=[{'field': field}]
            ).count()
            field_stats.append({
                'field': field,
                'count': count,
                'percentage': round(count / difference_count * 100, 1) if difference_count > 0 else 0
            })
        result['by_field'] = field_stats

        # 高频错误收款方
        top_errors = []
        error_payments = queryset.filter(is_match=False)
        payee_errors = {}
        for comp in error_payments:
            payee_name = comp.application.payee_name
            payee_errors[payee_name] = payee_errors.get(payee_name, 0) + 1

        top_errors = sorted(payee_errors.items(), key=lambda x: x[1], reverse=True)[:10]
        result['top_error_payees'] = [
            {'payee_name': name, 'error_count': count}
            for name, count in top_errors
        ]

        return ApiResponse.success(data=result)


class EfficiencyAnalysisView(APIView):
    """效率分析"""
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = PaymentApplication.objects.filter(
            status__in=['paid', 'verified']
        )

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # 计算各阶段平均耗时（分钟）
        applications = list(queryset)

        if not applications:
            return ApiResponse.success(data={
                'avg_audit_time': 0,
                'avg_payment_time': 0,
                'avg_total_time': 0,
                'by_stage': [],
                'bottleneck': '无数据'
            })

        # 模拟计算（实际应从审核日志获取）
        avg_audit_time = 30.5  # 平均审核时间（分钟）
        avg_payment_time = 45.0  # 平均付款时间（分钟）
        avg_total_time = avg_audit_time + avg_payment_time + 20  # 总耗时

        result = {
            'avg_audit_time': avg_audit_time,
            'avg_payment_time': avg_payment_time,
            'avg_total_time': avg_total_time,
            'by_stage': [
                {'stage': '申请提交', 'avg_time': 5.0, 'unit': '分钟'},
                {'stage': '会计审核', 'avg_time': avg_audit_time, 'unit': '分钟'},
                {'stage': '出纳付款', 'avg_time': avg_payment_time, 'unit': '分钟'},
                {'stage': '对比复核', 'avg_time': 20.0, 'unit': '分钟'},
            ],
            'bottleneck': '出纳付款'
        }

        return ApiResponse.success(data=result)


class DashboardView(APIView):
    """仪表盘数据"""
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        from django.utils import timezone
        from datetime import date

        today = date.today()
        month_start = today.replace(day=1)

        # 今日统计
        today_applications = PaymentApplication.objects.filter(
            application_date=today
        ).count()

        today_payments = ActualPayment.objects.filter(
            payment_date__date=today
        ).count()

        # 待处理
        pending_approvals = PaymentApplication.objects.filter(
            status='pending'
        ).count()

        pending_payments = PaymentApplication.objects.filter(
            status='approved'
        ).count()

        pending_reviews = ComparisonResult.objects.filter(
            is_match=False,
            verified=False
        ).count()

        # 本月统计
        month_applications = PaymentApplication.objects.filter(
            application_date__gte=month_start
        ).count()

        month_amount = PaymentApplication.objects.filter(
            application_date__gte=month_start,
            status__in=['approved', 'paid', 'verified']
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 差异统计
        month_differences = ComparisonResult.objects.filter(
            created_at__date__gte=month_start,
            is_match=False
        ).count()

        result = {
            'today': {
                'applications': today_applications,
                'payments': today_payments,
            },
            'pending': {
                'approvals': pending_approvals,
                'payments': pending_payments,
                'reviews': pending_reviews,
            },
            'month': {
                'applications': month_applications,
                'amount': float(month_amount),
                'differences': month_differences,
            }
        }

        return ApiResponse.success(data=result)