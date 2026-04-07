"""
用户管理后台
"""
from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'department', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['username', 'name', 'email']
    readonly_fields = ['created_at', 'updated_at']