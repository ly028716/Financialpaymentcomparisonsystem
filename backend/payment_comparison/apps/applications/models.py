"""
付款申请 Model
"""
from django.db import models
from decimal import Decimal


class PaymentApplication(models.Model):
    """付款申请表"""

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审核'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已拒绝'
        PAID = 'paid', '已付款'
        VERIFIED = 'verified', '已核验'

    application_no = models.CharField('申请单号', max_length=50, unique=True)
    department = models.CharField('申请部门', max_length=100)
    applicant = models.CharField('申请人', max_length=50)
    application_date = models.DateField('申请日期')

    # 收款方信息
    payee_name = models.CharField('收款方户名', max_length=200)
    payee_account = models.CharField('收款方账号', max_length=50)
    payee_bank = models.CharField('收款方开户行', max_length=200)

    # 付款信息
    amount = models.DecimalField('付款金额', max_digits=15, decimal_places=2)
    purpose = models.TextField('付款用途')
    attachments = models.JSONField('附件列表', default=list, blank=True)

    # 状态和标记
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    urgent = models.BooleanField('是否紧急', default=False)
    remark = models.TextField('备注', blank=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'payment_applications'
        verbose_name = '付款申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application_no']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['application_date']),
        ]

    def __str__(self):
        return f'{self.application_no} - {self.payee_name}'

    @property
    def amount_cn(self):
        """金额大写"""
        return self._convert_amount_to_cn(self.amount)

    @staticmethod
    def _convert_amount_to_cn(amount):
        """将数字金额转换为中文大写"""
        if not amount:
            return ''

        amount = Decimal(str(amount))
        units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
        digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']

        # 简化实现，生产环境需要完整实现
        integer_part = int(amount)
        decimal_part = int((amount - integer_part) * 100)

        result = ''

        if integer_part > 0:
            integer_str = str(integer_part)
            for i, digit in enumerate(integer_str):
                pos = len(integer_str) - i - 1
                result += digits[int(digit)] + units[pos]

        result += '元'

        if decimal_part > 0:
            jiao = decimal_part // 10
            fen = decimal_part % 10
            if jiao > 0:
                result += digits[jiao] + '角'
            if fen > 0:
                result += digits[fen] + '分'
        else:
            result += '整'

        return result

    def can_edit(self):
        """是否可编辑"""
        return self.status in [self.Status.DRAFT, self.Status.REJECTED]

    def can_delete(self):
        """是否可撤销"""
        return self.status == self.Status.PENDING


class AuditLog(models.Model):
    """审核日志"""

    class Action(models.TextChoices):
        CREATE = 'create', '创建'
        UPDATE = 'update', '更新'
        APPROVE = 'approve', '通过'
        REJECT = 'reject', '拒绝'
        CANCEL = 'cancel', '撤销'

    application = models.ForeignKey(
        PaymentApplication,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name='申请单'
    )
    action = models.CharField('操作类型', max_length=20, choices=Action.choices)
    operator = models.CharField('操作人', max_length=50)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审核日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application.application_no} - {self.get_action_display()}'