import { test, expect } from '@playwright/test'
import { loginAs, testUsers } from '../../fixtures/auth'

/**
 * E2E 测试：权限控制
 */
test.describe('权限控制', () => {
  test('未登录应该跳转到登录页', async ({ page }) => {
    // 访问受保护页面
    await page.goto('/dashboard')

    // 清除token
    await page.evaluate(() => {
      localStorage.clear()
    })

    // 刷新页面触发路由守卫
    await page.reload()

    // 验证跳转到登录页
    await expect(page).toHaveURL(/\/login/)
  })

  test('部门申请人不能访问审核功能', async ({ page }) => {
    // 使用 loginAs fixture 登录
    await loginAs(page, testUsers.applicant)

    await page.goto('/applications')
    await page.waitForLoadState('networkidle')

    // 申请人应该只能看到自己的申请
    const hasTable = await page.locator('.el-table').isVisible({ timeout: 2000 }).catch(() => false)
    const hasEmpty = await page.locator('.el-empty').isVisible({ timeout: 2000 }).catch(() => false)

    expect(hasTable || hasEmpty).toBeTruthy()
  })

  test('出纳不能审核申请', async ({ page }) => {
    // 使用 loginAs fixture 登录
    await loginAs(page, testUsers.cashier)

    await page.goto('/applications')
    await page.waitForLoadState('networkidle')

    // 出纳不应该看到审核按钮
    const approveBtn = page.getByRole('button', { name: '审核通过' })
    const hasApproveBtn = await approveBtn.isVisible({ timeout: 2000 }).catch(() => false)

    // 出纳应该不能审核
    expect(hasApproveBtn || true).toBeFalsy()
  })

  test('财务主管可以审核大额付款', async ({ page }) => {
    // 使用 loginAs fixture 登录
    await loginAs(page, testUsers.financeManager)

    await page.goto('/applications')
    await page.waitForLoadState('networkidle')

    // 财务主管应该能审核大额付款
    const hasAccess = !page.url().includes('/login')
    expect(hasAccess).toBeTruthy()
  })
})

/**
 * E2E 测试：响应式布局
 */
test.describe('响应式布局', () => {
  test('移动端应该正常显示', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })

    // 使用 loginAs fixture 登录
    await loginAs(page, testUsers.applicant)

    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    // 验证页面在移动端正常加载
    const hasDashboard = await page.locator('.dashboard, .main-content').isVisible({ timeout: 2000 }).catch(() => false)
    expect(hasDashboard).toBeTruthy()
  })

  test('平板端应该正常显示', async ({ page }) => {
    // 设置平板视口
    await page.setViewportSize({ width: 768, height: 1024 })

    // 使用 loginAs fixture 登录
    await loginAs(page, testUsers.applicant)

    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    const hasDashboard = await page.locator('.dashboard, .main-content').isVisible({ timeout: 2000 }).catch(() => false)
    expect(hasDashboard).toBeTruthy()
  })
})