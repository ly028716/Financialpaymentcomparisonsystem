"""
Django 应用配置
"""
from django.apps import AppConfig


class PaymentComparisonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment_comparison'
    verbose_name = '财务付款对比系统'