"""
报表统计URL配置
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('payment-stats/', views.PaymentStatsView.as_view(), name='payment_stats'),
    path('difference-analysis/', views.DifferenceAnalysisView.as_view(), name='difference_analysis'),
    path('efficiency-analysis/', views.EfficiencyAnalysisView.as_view(), name='efficiency_analysis'),
]