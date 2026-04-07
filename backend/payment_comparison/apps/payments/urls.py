"""
实际付款URL配置
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListAPIView.as_view(), name='list'),
    path('pending/', views.PendingPaymentListView.as_view(), name='pending'),
    path('batch/', views.BatchPaymentView.as_view(), name='batch'),
    path('ocr/', views.OCRAPIView.as_view(), name='ocr'),
    path('<int:id>/', views.PaymentDetailAPIView.as_view(), name='detail'),
]