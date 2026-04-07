"""
付款申请URL配置
"""
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.ApplicationListAPIView.as_view(), name='list'),
    path('my/', views.MyApplicationListView.as_view(), name='my'),
    path('pending/', views.PendingApplicationListView.as_view(), name='pending'),
    path('export/', views.ExportApplicationView.as_view(), name='export'),
    path('batch-approve/', views.BatchApproveView.as_view(), name='batch_approve'),
    path('<int:id>/', views.ApplicationDetailAPIView.as_view(), name='detail'),
    path('<int:id>/approve/', views.ApproveApplicationView.as_view(), name='approve'),
    path('<int:id>/reject/', views.RejectApplicationView.as_view(), name='reject'),
]