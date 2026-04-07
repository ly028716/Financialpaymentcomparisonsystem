# E2E 测试报告

## 测试概览

使用 Playwright 进行端到端测试，覆盖财务付款对比系统的核心用户流程。

---

## 测试文件清单

| 测试文件 | 测试场景数 | 说明 |
|---------|-----------|------|
| `tests/e2e/auth/login.spec.ts` | 4 | 登录流程测试 |
| `tests/e2e/applications/list.spec.ts` | 5 | 付款申请流程测试 |
| `tests/e2e/approval/review.spec.ts` | 4 | 审核流程测试 |
| `tests/e2e/permissions/access.spec.ts` | 5 | 权限控制测试 |
| **总计** | **18** | - |

---

## 测试场景详情

### 1. 认证流程 (`auth/login.spec.ts`)

```
✓ 应该显示登录表单
✓ 空表单提交应该显示验证错误
✓ 错误的凭证应该显示错误提示
✓ 成功登录应该跳转到仪表盘
```

### 2. 付款申请流程 (`applications/list.spec.ts`)

```
✓ 应该显示申请列表页面
✓ 应该能筛选申请列表
✓ 应该能跳转到创建申请页面
✓ 创建申请表单验证
✓ 应该能填写并提交申请
```

### 3. 审核流程 (`approval/review.spec.ts`)

```
✓ 会计应该能看到待审核列表
✓ 应该能查看申请详情
✓ 详情页应该显示审核按钮
✓ 仪表盘统计卡片应该显示
```

### 4. 权限控制 (`permissions/access.spec.ts`)

```
✓ 未登录应该跳转到登录页
✓ 部门申请人不能访问审核功能
✓ 出纳不能审核申请
✓ 财务主管可以审核大额付款
✓ 移动端应该正常显示
```

---

## 浏览器覆盖

| 浏览器 | 状态 |
|--------|------|
| Chrome (Chromium) | ✅ |
| Firefox | ✅ |
| Safari (WebKit) | ✅ |
| Mobile Chrome | 可配置 |
| Mobile Safari | 可配置 |

---

## 运行测试

### 安装依赖

```bash
cd frontend
npm install
npx playwright install
```

### 运行所有测试

```bash
npm run test:e2e
```

### 运行特定测试

```bash
npx playwright test tests/e2e/auth/login.spec.ts
```

### 调试模式

```bash
npx playwright test --debug
```

### 查看报告

```bash
npx playwright show-report
```

---

## 测试工件

测试运行时自动生成：

| 工件类型 | 生成条件 | 存放位置 |
|---------|---------|---------|
| HTML 报告 | 每次运行 | `playwright-report/` |
| 截图 | 测试失败 | `test-results/` |
| 视频 | 测试失败 | `test-results/` |
| Trace | 首次重试 | `test-results/` |

---

## Page Object 模式

建议使用 Page Object Model 提高测试可维护性：

```typescript
// tests/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login')
  }

  async login(username: string, password: string) {
    await this.page.fill('[data-testid="username-input"]', username)
    await this.page.fill('[data-testid="password-input"]', password)
    await this.page.click('[data-testid="login-btn"]')
  }
}
```

---

## CI/CD 集成

### GitHub Actions 配置

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 最佳实践

### ✅ 推荐做法

1. **使用 data-testid 选择器** - 稳定且不依赖样式
2. **等待 API 响应** - 不使用固定超时
3. **Page Object Model** - 提高可维护性
4. **独立测试** - 每个测试应该自包含
5. **清理数据** - 测试后清理创建的数据

### ❌ 避免做法

1. **不要依赖 CSS 类名** - 可能会改变
2. **不要使用固定等待** - 使用智能等待
3. **不要测试实现细节** - 测试用户行为
4. **不要在测试间共享状态** - 每个测试应该独立

---

## 测试覆盖的关键流程

```
┌─────────────────────────────────────────────────────────────┐
│                    用户登录流程                              │
│  访问登录页 → 输入凭证 → 提交 → 验证跳转                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    付款申请流程                              │
│  查看列表 → 创建申请 → 填写表单 → 提交 → 验证状态             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    审核流程                                  │
│  查看待审核 → 查看详情 → 审核通过/拒绝 → 验证状态更新         │
└─────────────────────────────────────────────────────────────┘
```

---

## 测试状态

```
╔══════════════════════════════════════════════════════════════╗
║                    E2E 测试套件状态                          ║
╠══════════════════════════════════════════════════════════════╣
║ 总测试数:    18                                             ║
║ 测试文件:    4                                              ║
║ 浏览器:      Chrome, Firefox, Safari                        ║
║ 状态:        ✅ 就绪                                         ║
╚══════════════════════════════════════════════════════════════╝
```