# 安全漏洞修复记录

**修复日期：** 2026-04-06
**修复人：** Claude Code

---

## 修复的问题

### 🔴 CRITICAL - IsAccountant 权限类实现错误

**问题：**
`IsAccountant` 权限类错误地检查了 `Role.CASHIER` 而不是 `Role.ACCOUNTANT`，导致：
- 会计用户无法访问应有的接口
- 出纳用户可以访问会计权限的接口（权限泄露）
- Admin用户无法访问会计接口

**修复：**
```python
# 修复前
class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == Role.CASHIER  # ❌ 错误
        )

# 修复后
class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.ACCOUNTANT, Role.ADMIN]  # ✅ 正确
```

**影响范围：**
- ✅ 会计用户现在可以正常审核申请
- ✅ Admin用户可以访问所有会计接口
- ✅ 出纳用户不再能访问会计接口

---

### 🟠 HIGH - 用户管理接口无权限保护

**问题：**
`UserListAPIView` 和 `UserDetailAPIView` 完全没有权限检查，任何人（包括未登录用户）都可以：
- 查看所有用户列表
- 创建新用户
- 修改任意用户信息
- 删除任意用户

**修复：**
```python
# 修复前
class UserListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # ❌ 无权限检查

# 修复后
class UserListAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # ✅ 仅管理员可访问
```

**影响范围：**
- ✅ 用户管理接口现在仅管理员可访问
- ✅ 防止了信息泄露和权限提升攻击

---

### 🟠 HIGH - 单一角色权限类未包含Admin

**问题：**
`IsApplicant`、`IsCashier`、`IsFinanceManager` 等权限类只检查单一角色，不允许Admin访问。

**修复：**
所有单一角色权限类现在都包含Admin：
```python
# 修复前
class IsApplicant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == Role.APPLICANT  # ❌ 只允许申请人
        )

# 修复后
class IsApplicant(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in [Role.APPLICANT, Role.ADMIN]  # ✅ 允许申请人和管理员
```

**影响范围：**
- ✅ Admin用户现在可以访问所有接口
- ✅ 符合"管理员拥有所有权限"的设计原则

---

## 修复后的权限矩阵

| 接口 | 申请人 | 会计 | 出纳 | 财务主管 | 管理员 |
|------|--------|------|------|---------|--------|
| 创建申请 | ✅ | ❌ | ❌ | ❌ | ✅ |
| 查看申请 | ✅(自己) | ✅ | ✅ | ✅ | ✅ |
| 审核申请 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 创建付款 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 查看对比 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 人工复核 | ❌ | ❌ | ❌ | ✅ | ✅ |
| 查看报表 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 用户管理 | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 测试验证

### 手动测试步骤

1. **测试Admin用户：**
```bash
# 登录admin账号
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin123"
}

# 测试访问各个接口
GET /api/applications/          # ✅ 应该成功
GET /api/applications/pending/  # ✅ 应该成功
GET /api/payments/              # ✅ 应该成功
GET /api/comparison/            # ✅ 应该成功
GET /api/reports/dashboard/     # ✅ 应该成功
GET /api/users/                 # ✅ 应该成功
```

2. **测试会计用户：**
```bash
# 登录会计账号
POST /api/auth/login/
{
  "username": "accountant",
  "password": "password"
}

# 测试访问各个接口
GET /api/applications/pending/  # ✅ 应该成功
PUT /api/applications/1/approve/ # ✅ 应该成功
GET /api/payments/              # ❌ 应该返回403
GET /api/users/                 # ❌ 应该返回403
```

3. **测试出纳用户：**
```bash
# 登录出纳账号
POST /api/auth/login/
{
  "username": "cashier",
  "password": "password"
}

# 测试访问各个接口
POST /api/payments/             # ✅ 应该成功
GET /api/applications/pending/  # ❌ 应该返回403
GET /api/users/                 # ❌ 应该返回403
```

4. **测试未登录用户：**
```bash
# 不带token访问
GET /api/applications/          # ❌ 应该返回401
GET /api/users/                 # ❌ 应该返回401
```

---

## 后续建议

### 1. 添加自动化测试
```python
# tests/test_permissions_fixed.py
def test_admin_can_access_all_endpoints():
    """测试Admin可以访问所有接口"""
    admin = create_user(role='admin')
    client.force_authenticate(user=admin)

    assert client.get('/api/applications/').status_code == 200
    assert client.get('/api/payments/').status_code == 200
    assert client.get('/api/comparison/').status_code == 200
    assert client.get('/api/users/').status_code == 200

def test_accountant_permissions():
    """测试会计权限"""
    accountant = create_user(role='accountant')
    client.force_authenticate(user=accountant)

    assert client.get('/api/applications/pending/').status_code == 200
    assert client.put('/api/applications/1/approve/').status_code == 200
    assert client.post('/api/payments/').status_code == 403  # 不能创建付款
    assert client.get('/api/users/').status_code == 403  # 不能管理用户
```

### 2. 代码审查清单
- [ ] 所有视图都有明确的 `permission_classes`
- [ ] 单一角色权限类都包含Admin
- [ ] 敏感接口（用户管理、系统配置）仅Admin可访问
- [ ] 权限测试覆盖率 ≥ 90%

### 3. 安全加固建议
- [ ] 启用Django的CSRF保护
- [ ] 配置CORS白名单
- [ ] 启用请求频率限制（Rate Limiting）
- [ ] 记录所有权限拒绝事件到审计日志
- [ ] 定期审查权限配置

---

## 修复文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| `common/permissions.py` | 修复4个权限类 | +16/-12 |
| `apps/users/views.py` | 添加权限保护 | +10/-2 |

---

**修复完成！** 🎉

所有CRITICAL和HIGH级别的安全问题已修复。建议立即部署到测试环境验证。
