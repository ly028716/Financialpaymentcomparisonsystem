"""
实际付款 Model
"""
from django.db import models


class ActualPayment(models.Model):
    """实际付款记录表"""

    class Channel(models.TextChoices):
        ONLINE = 'online', '网银转账'
        COUNTER = 'counter', '柜台转账'
        CHECK = 'check', '支票'
        ACCEPTANCE = 'acceptance', '承兑汇票'
        OTHER = 'other', '其他'

    payment_no = models.CharField('付款单号', max_length=50, unique=True)
    application = models.ForeignKey(
        'applications.PaymentApplication',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='关联申请单'
    )

    # 实际付款信息
    actual_payee_name = models.CharField('实际收款户名', max_length=200)
    actual_payee_account = models.CharField('实际收款账号', max_length=50)
    actual_payee_bank = models.CharField('实际开户行', max_length=200, blank=True)
    actual_amount = models.DecimalField('实际付款金额', max_digits=15, decimal_places=2)

    # 付款详情
    payment_channel = models.CharField(
        '付款渠道',
        max_length=50,
        choices=Channel.choices
    )
    bank_serial_no = models.CharField('银行流水号', max_length=100, blank=True)
    payment_voucher = models.JSONField('付款凭证', default=list, blank=True)

    # 经办人信息
    operator = models.CharField('经办人', max_length=50)
    payment_date = models.DateTimeField('付款时间')

    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'actual_payments'
        verbose_name = '实际付款记录'
        verbose_name_plural = verbose_name
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_no']),
            models.Index(fields=['application']),
            models.Index(fields=['payment_date']),
        ]

    def __str__(self):
        return f'{self.payment_no} - {self.actual_payee_name}'