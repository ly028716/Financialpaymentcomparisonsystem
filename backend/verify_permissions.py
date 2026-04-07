#!/usr/bin/env python
"""
权限修复快速验证脚本

使用方法：
    cd backend
    python verify_permissions.py
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_comparison.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from payment_comparison.common.permissions import (
    IsApplicant, IsAccountant, IsCashier, IsFinanceManager, IsAdmin,
    Role
)

User = get_user_model()


class MockRequest:
    """模拟请求对象"""
    def __init__(self, user):
        self.user = user


def test_permission_class(permission_class, user, expected_result):
    """测试权限类"""
    request = MockRequest(user)
    permission = permission_class()
    result = permission.has_permission(request, None)

    status = "✅ PASS" if result == expected_result else "❌ FAIL"
    return status, result


def main():
    print("=" * 80)
    print("权限修复验证脚本")
    print("=" * 80)
    print()

    # 创建测试用户
    print("📝 创建测试用户...")

    # 清理旧数据
    User.objects.filter(username__in=['test_admin', 'test_accountant', 'test_cashier', 'test_applicant']).delete()

    admin = User.objects.create_user(
        username='test_admin',
        password='password',
        name='测试管理员',
        email='admin@test.com',
        department='管理部',
        role='admin'
    )

    accountant = User.objects.create_user(
        username='test_accountant',
        password='password',
        name='测试会计',
        email='accountant@test.com',
        department='财务部',
        role='accountant'
    )

    cashier = User.objects.create_user(
        username='test_cashier',
        password='password',
        name='测试出纳',
        email='cashier@test.com',
        department='财务部',
        role='cashier'
    )

    applicant = User.objects.create_user(
        username='test_applicant',
        password='password',
        name='测试申请人',
        email='applicant@test.com',
        department='技术部',
        role='applicant'
    )

    print(f"✅ 创建了4个测试用户")
    print()

    # 测试用例
    test_cases = [
        # (权限类, 用户, 期望结果, 描述)
        (IsAccountant, accountant, True, "会计用户访问会计权限"),
        (IsAccountant, admin, True, "管理员访问会计权限"),
        (IsAccountant, cashier, False, "出纳用户访问会计权限（应拒绝）"),
        (IsAccountant, applicant, False, "申请人访问会计权限（应拒绝）"),

        (IsCashier, cashier, True, "出纳用户访问出纳权限"),
        (IsCashier, admin, True, "管理员访问出纳权限"),
        (IsCashier, accountant, False, "会计用户访问出纳权限（应拒绝）"),

        (IsApplicant, applicant, True, "申请人访问申请人权限"),
        (IsApplicant, admin, True, "管理员访问申请人权限"),
        (IsApplicant, accountant, False, "会计访问申请人权限（应拒绝）"),

        (IsAdmin, admin, True, "管理员访问管理员权限"),
        (IsAdmin, accountant, False, "会计访问管理员权限（应拒绝）"),
    ]

    print("🧪 开始测试权限类...")
    print()

    passed = 0
    failed = 0

    for permission_class, user, expected, description in test_cases:
        status, result = test_permission_class(permission_class, user, expected)
        print(f"{status} {description}")
        print(f"   权限类: {permission_class.__name__}")
        print(f"   用户: {user.name} (role={user.role})")
        print(f"   期望: {expected}, 实际: {result}")
        print()

        if status.startswith("✅"):
            passed += 1
        else:
            failed += 1

    # 测试关键修复点
    print("=" * 80)
    print("🔍 验证关键修复点")
    print("=" * 80)
    print()

    # 1. IsAccountant 不再检查 CASHIER
    print("1️⃣  验证 IsAccountant 修复（最严重的bug）")
    status1, _ = test_permission_class(IsAccountant, accountant, True)
    status2, _ = test_permission_class(IsAccountant, cashier, False)

    if status1.startswith("✅") and status2.startswith("✅"):
        print("   ✅ IsAccountant 已正确修复")
        print("   - 会计用户可以访问 ✅")
        print("   - 出纳用户被拒绝 ✅")
    else:
        print("   ❌ IsAccountant 仍有问题")
    print()

    # 2. Admin 可以访问所有权限
    print("2️⃣  验证 Admin 可以访问所有权限")
    admin_tests = [
        (IsApplicant, "申请人权限"),
        (IsAccountant, "会计权限"),
        (IsCashier, "出纳权限"),
        (IsFinanceManager, "财务主管权限"),
        (IsAdmin, "管理员权限"),
    ]

    all_admin_pass = True
    for perm_class, name in admin_tests:
        status, _ = test_permission_class(perm_class, admin, True)
        if status.startswith("✅"):
            print(f"   ✅ Admin 可以访问 {name}")
        else:
            print(f"   ❌ Admin 无法访问 {name}")
            all_admin_pass = False

    if all_admin_pass:
        print("   ✅ Admin 权限修复成功")
    else:
        print("   ❌ Admin 权限仍有问题")
    print()

    # 总结
    print("=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    print(f"总测试数: {passed + failed}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print()

    if failed == 0:
        print("🎉 所有测试通过！权限修复成功！")
        print()
        print("✅ 关键修复验证：")
        print("   1. IsAccountant 现在正确检查 ACCOUNTANT 角色")
        print("   2. 所有单一角色权限类都允许 Admin 访问")
        print("   3. 权限隔离正常工作（会计不能访问出纳接口等）")
        return 0
    else:
        print("⚠️  部分测试失败，请检查权限配置")
        return 1

    # 清理测试用户
    print()
    print("🧹 清理测试数据...")
    User.objects.filter(username__in=['test_admin', 'test_accountant', 'test_cashier', 'test_applicant']).delete()
    print("✅ 清理完成")


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ 验证脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
