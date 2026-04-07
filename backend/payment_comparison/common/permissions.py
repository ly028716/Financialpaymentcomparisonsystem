"""
自定义权限类
基于角色的权限控制 (RBAC)
"""
from rest_framework.permissions import BasePermission


# 角色常量定义
class Role:
    """用户角色定义"""

    APPLICANT = 'applicant'          # 部门申请人
    ACCOUNTANT = 'accountant'        # 会计
    CASHIER = 'cashier'              # 出纳
    FINANCE_MANAGER = 'finance_manager'  # 财务主管
    ADMIN = 'admin'                  # 系统管理员


class IsApplicant(BasePermission):
    """部门申请人权限（管理员也可访问）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.APPLICANT, Role.ADMIN]


class IsAccountant(BasePermission):
    """会计权限（管理员也可访问）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.ACCOUNTANT, Role.ADMIN]


class IsCashier(BasePermission):
    """出纳权限（管理员也可访问）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.CASHIER, Role.ADMIN]


class IsFinanceManager(BasePermission):
    """财务主管权限（管理员也可访问）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.FINANCE_MANAGER, Role.ADMIN]


class IsAdmin(BasePermission):
    """系统管理员权限"""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == Role.ADMIN
        )


class CanApproveLargeAmount(BasePermission):
    """可以审批大额付款（≥10万）的权限

    仅财务主管和管理员可以审批
    """

    LARGE_AMOUNT_THRESHOLD = 100000  # 10万元

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, 'role', None)
        return role in [Role.FINANCE_MANAGER, Role.ADMIN]


class IsAccountantOrFinanceManager(BasePermission):
    """会计或财务主管权限"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, 'role', None)
        return role in [Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN]


class IsCashierOrAdmin(BasePermission):
    """出纳或管理员权限"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, 'role', None)
        return role in [Role.CASHIER, Role.ADMIN]


class IsOwnerOrAdmin(BasePermission):
    """资源所有者或管理员权限

    用于检查用户是否是资源的所有者
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # 管理员拥有所有权限
        if getattr(request.user, 'role', None) == Role.ADMIN:
            return True

        # 检查是否是资源所有者
        owner_field = getattr(obj, 'applicant', None) or getattr(obj, 'created_by', None)
        if owner_field:
            return owner_field == request.user

        return False


class IsOwnerOrAccountantOrAbove(BasePermission):
    """资源所有者或会计及以上权限

    用于申请查看等场景
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, 'role', None)

        # 管理员和财务主管拥有所有权限
        if role in [Role.ADMIN, Role.FINANCE_MANAGER]:
            return True

        # 会计可以查看所有申请
        if role == Role.ACCOUNTANT:
            return True

        # 出纳可以查看待付款申请
        if role == Role.CASHIER:
            return True

        # 检查是否是资源所有者
        owner_field = getattr(obj, 'applicant', None) or getattr(obj, 'created_by', None)
        if owner_field:
            return owner_field == request.user

        return False


# 权限映射表（用于API文档和前端）
PERMISSION_MATRIX = {
    'application:create': [Role.APPLICANT, Role.ADMIN],
    'application:read': [Role.APPLICANT, Role.ACCOUNTANT, Role.CASHIER, Role.FINANCE_MANAGER, Role.ADMIN],
    'application:update': [Role.APPLICANT, Role.ADMIN],
    'application:delete': [Role.APPLICANT, Role.ADMIN],
    'application:approve': [Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN],
    'application:approve_large': [Role.FINANCE_MANAGER, Role.ADMIN],
    'application:export': [Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN],
    'payment:create': [Role.CASHIER, Role.ADMIN],
    'payment:read': [Role.CASHIER, Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN],
    'payment:ocr': [Role.CASHIER, Role.ADMIN],
    'comparison:read': [Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN],
    'comparison:verify': [Role.FINANCE_MANAGER, Role.ADMIN],
    'reports:read': [Role.ACCOUNTANT, Role.FINANCE_MANAGER, Role.ADMIN],
    'users:manage': [Role.ADMIN],
}


def has_permission(user, permission_name):
    """
    检查用户是否拥有指定权限

    Args:
        user: 用户对象
        permission_name: 权限名称（如 'application:create'）

    Returns:
        bool: 是否拥有权限
    """
    if not user or not user.is_authenticated:
        return False

    role = getattr(user, 'role', None)
    if not role:
        return False

    allowed_roles = PERMISSION_MATRIX.get(permission_name, [])
    return role in allowed_roles