# 付款申请测试说明

## 测试账号

系统已创建以下测试用户：

| 用户名 | 密码 | 角色 | 部门 |
|--------|------|------|------|
| admin | admin123 | 系统管理员 | 信息部 |
| applicant | test123 | 部门申请人 | 技术部 |
| accountant | test123 | 会计 | 财务部 |
| cashier | test123 | 出纳 | 财务部 |
| manager | test123 | 财务主管 | 财务部 |

## 测试银行卡号

系统使用 **Luhn 算法**验证银行卡号，请使用以下有效的测试账号：

### 推荐测试账号

```
6222021234567894  (中国工商银行)
6228481234567893  (中国农业银行)
6217001234567896  (中国建设银行)
6216611234567899  (中国银行)
6225881234567892  (招商银行)
```

### 银行卡号规则

- **长度**: 15-19 位数字
- **验证**: 必须通过 Luhn 算法校验
- **格式**: 纯数字，不含空格或其他字符

## 创建付款申请测试流程

### 1. 登录系统

使用 `applicant / test123` 登录（部门申请人角色）

### 2. 填写申请表单

- **收款方户名**: 测试公司（2-200字符，支持中英文、数字、括号）
- **收款方账号**: 6222021234567894（使用上面的测试账号）
- **开户行**: 中国工商银行（2-200字符）
- **付款金额**: 1000.50（0.01 - 999,999,999.99）
- **付款用途**: 测试付款用途说明（2-500字符）
- **是否紧急**: 否
- **备注**: 可选

### 3. 提交申请

点击"提交申请"按钮，系统会：
1. 前端验证所有字段（包括 Luhn 算法）
2. 提交到后端 API
3. 后端再次验证并创建申请
4. 返回申请单号（格式：FK20260407XXXX）

### 4. 查看申请

提交成功后会跳转到申请列表页面，可以看到刚创建的申请。

## 常见问题

### Q: 为什么提示"账号校验失败"？

A: 银行卡号必须通过 Luhn 算法验证。请使用上面提供的测试账号，或使用工具生成有效账号。

### Q: 如何生成新的测试账号？

A: 可以使用后端脚本生成：

```bash
cd backend
./venv/Scripts/python -c "
from payment_comparison.apps.applications.utils import calculate_luhn_checksum

# 生成工商银行测试账号
partial = '622202' + '1234567890'  # 前6位是银行代码，后面随意
checksum = calculate_luhn_checksum(partial)
print(f'有效账号: {partial}{checksum}')
"
```

### Q: 前端如何生成测试账号？

A: 前端提供了工具函数：

```typescript
import { generateTestBankAccount } from '@/utils/bankAccount'

// 生成随机测试账号
const testAccount = generateTestBankAccount()

// 生成指定银行的测试账号
const icbcAccount = generateTestBankAccount('622202') // 工商银行
```

### Q: 会计/出纳能创建申请吗？

A: 不能。只有"部门申请人"角色可以创建付款申请。

### Q: 金额输入框为什么是空的？

A: 这是正常的。初始值设为 `undefined`，避免默认值 0 导致验证错误。

## 审批流程测试

### 1. 会计审核

使用 `accountant / test123` 登录，在"待审核"列表中审核申请。

### 2. 出纳付款

使用 `cashier / test123` 登录，录入付款记录。

### 3. 对比验证

系统自动对比申请和付款记录，标记差异。

### 4. 主管复核

使用 `manager / test123` 登录，查看对比结果并处理异常。

## API 测试

### 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"applicant","password":"test123"}'
```

### 创建申请

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/applications/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "payee_name": "测试公司",
    "payee_account": "6222021234567894",
    "payee_bank": "中国工商银行",
    "amount": 1000.50,
    "purpose": "测试付款用途",
    "urgent": false,
    "remark": "测试备注"
  }'
```

## 开发环境配置

### 前端

- 运行端口: 3001
- API 代理: `/api` -> `http://localhost:8000`

### 后端

- 运行端口: 8000
- 数据库: SQLite (db.sqlite3)
- 调试模式: 已启用

## 注意事项

1. **不要在生产环境使用测试账号**
2. **测试银行卡号仅用于开发测试**
3. **定期清理测试数据**
4. **生产环境应使用真实的银行卡号验证**
