"""
对比结果 Model
"""
from django.db import models


class ComparisonResult(models.Model):
    """对比结果表"""

    application = models.ForeignKey(
        'applications.PaymentApplication',
        on_delete=models.CASCADE,
        related_name='comparison_results',
        verbose_name='申请单'
    )
    payment = models.ForeignKey(
        'payments.ActualPayment',
        on_delete=models.CASCADE,
        related_name='comparison_results',
        verbose_name='付款记录'
    )

    # 对比结果
    is_match = models.BooleanField('是否匹配', default=False)
    differences = models.JSONField('差异详情', default=list, blank=True)

    # 复核信息
    verified = models.BooleanField('是否已复核', default=False)
    verified_by = models.CharField('复核人', max_length=50, blank=True)
    verified_at = models.DateTimeField('复核时间', null=True, blank=True)
    verification_note = models.TextField('复核说明', blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'comparison_results'
        verbose_name = '对比结果'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_match']),
            models.Index(fields=['verified']),
        ]

    def __str__(self):
        status = '匹配' if self.is_match else '不匹配'
        return f'{self.application.application_no} - {status}'

    @property
    def severity(self):
        """获取最高严重程度"""
        if not self.differences:
            return None

        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        for severity in severity_order:
            for diff in self.differences:
                if diff.get('severity') == severity:
                    return severity
        return 'LOW'


class AlertNotification(models.Model):
    """差异预警通知"""

    class Severity(models.TextChoices):
        CRITICAL = 'CRITICAL', '严重'
        HIGH = 'HIGH', '高'
        MEDIUM = 'MEDIUM', '中'
        LOW = 'LOW', '低'

    class Status(models.TextChoices):
        PENDING = 'pending', '待处理'
        SENT = 'sent', '已发送'
        FAILED = 'failed', '发送失败'
        READ = 'read', '已读'

    comparison = models.ForeignKey(
        ComparisonResult,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='对比结果'
    )

    severity = models.CharField(
        '严重程度',
        max_length=20,
        choices=Severity.choices
    )
    title = models.CharField('标题', max_length=200)
    message = models.TextField('消息内容')
    recipients = models.JSONField('接收人列表', default=list)

    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    sent_at = models.DateTimeField('发送时间', null=True, blank=True)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'alert_notifications'
        verbose_name = '差异预警通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.get_severity_display()}'