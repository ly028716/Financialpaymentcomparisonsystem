"""
创建测试用户脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_comparison.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from payment_comparison.apps.users.models import User

def create_test_users():
    """创建测试用户"""

    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'name': '系统管理员',
            'email': 'admin@example.com',
            'department': '信息部',
            'role': 'admin',
        },
        {
            'username': 'applicant',
            'password': 'test123',
            'name': '张三',
            'email': 'zhangsan@example.com',
            'department': '技术部',
            'role': 'applicant',
        },
        {
            'username': 'accountant',
            'password': 'test123',
            'name': '李会计',
            'email': 'accountant@example.com',
            'department': '财务部',
            'role': 'accountant',
        },
        {
            'username': 'cashier',
            'password': 'test123',
            'name': '王出纳',
            'email': 'cashier@example.com',
            'department': '财务部',
            'role': 'cashier',
        },
        {
            'username': 'manager',
            'password': 'test123',
            'name': '赵主管',
            'email': 'manager@example.com',
            'department': '财务部',
            'role': 'finance_manager',
        },
    ]

    for user_data in users_data:
        username = user_data['username']
        password = user_data.pop('password')

        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_data
        )

        if created:
            user.set_password(password)
            user.save()
            print(f"✅ 创建用户: {username} ({user_data['role']})")
        else:
            print(f"⚠️  用户已存在: {username}")

    print("\n测试用户创建完成!")
    print("=" * 50)
    print("登录信息:")
    print("  管理员: admin / admin123")
    print("  申请人: applicant / test123")
    print("  会计:   accountant / test123")
    print("  出纳:   cashier / test123")
    print("  主管:   manager / test123")
    print("=" * 50)


if __name__ == '__main__':
    create_test_users()