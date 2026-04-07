"""
用户 URL 配置
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListAPIView.as_view(), name='list'),
    path('<int:id>/', views.UserDetailAPIView.as_view(), name='detail'),
]