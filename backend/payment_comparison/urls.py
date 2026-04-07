"""
URL 配置
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('payment_comparison.apps.authentication.urls')),
    path('api/users/', include('payment_comparison.apps.users.urls')),
    path('api/applications/', include('payment_comparison.apps.applications.urls')),
    path('api/payments/', include('payment_comparison.apps.payments.urls')),
    path('api/comparison/', include('payment_comparison.apps.comparison.urls')),
    path('api/reports/', include('payment_comparison.apps.reports.urls')),
    path('api/files/', include('payment_comparison.apps.files.urls')),
]