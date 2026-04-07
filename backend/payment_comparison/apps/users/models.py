"""
用户 Model
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""

    class Role(models.TextChoices):
        APPLICANT = 'applicant', '部门申请人'
        ACCOUNTANT = 'accountant', '会计'
        CASHIER = 'cashier', '出纳'
        FINANCE_MANAGER = 'finance_manager', '财务主管'
        ADMIN = 'admin', '系统管理员'

    name = models.CharField('姓名', max_length=50)
    email = models.EmailField('邮箱', unique=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    department = models.CharField('部门', max_length=100)
    role = models.CharField(
        '角色',
        max_length=20,
        choices=Role.choices,
        default=Role.APPLICANT
    )
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}({self.username})'

    @property
    def is_applicant(self):
        return self.role == self.Role.APPLICANT

    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT

    @property
    def is_cashier(self):
        return self.role == self.Role.CASHIER

    @property
    def is_finance_manager(self):
        return self.role == self.Role.FINANCE_MANAGER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN