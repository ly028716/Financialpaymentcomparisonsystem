"""
对比结果URL配置
"""
from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('', views.ComparisonListAPIView.as_view(), name='list'),
    path('trigger/', views.TriggerComparisonView.as_view(), name='trigger'),
    path('differences/', views.DifferenceListView.as_view(), name='differences'),
    path('alerts/', views.AlertNotificationListView.as_view(), name='alerts'),
    path('alerts/<int:id>/read/', views.AlertNotificationReadView.as_view(), name='alert_read'),
    path('<int:id>/', views.ComparisonDetailAPIView.as_view(), name='detail'),
    path('<int:id>/verify/', views.VerifyComparisonView.as_view(), name='verify'),
]