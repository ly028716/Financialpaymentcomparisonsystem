"""
文件管理URL配置
"""
from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    path('<str:file_id>/download/', views.FileDownloadView.as_view(), name='download'),
    path('<str:file_id>/', views.FileDeleteView.as_view(), name='delete'),
]