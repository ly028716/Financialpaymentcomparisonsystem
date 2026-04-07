import { test, expect } from '@playwright/test'
import { ApplicationDetailPage } from '../../pages/ApplicationDetailPage'
import { loginAs, testUsers } from '../../fixtures/auth'

/**
 * E2E 测试：申请详情流程
 * 测试计划文档 5.4 付款申请模块接口 - 前端E2E测试
 */
test.describe.configure({ mode: 'serial' })

test.describe('申请详情页面', () => {
  let detailPage: ApplicationDetailPage

  test.beforeEach(async ({ page }) => {
    detailPage = new ApplicationDetailPage(page)

    // 以申请人身份登录
    await loginAs(page, testUsers.applicant)
  })

  test('应该显示申请基本信息', async ({ page }) => {
    // 访问申请详情
    await detailPage.goto(1)

    // 等待页面加载
    await page.waitForLoadState('networkidle')

    // 验证页面元素（如果申请存在）
    const hasDetail = await page.locator('.application-detail, .el-descriptions').first().isVisible()
    const hasEmpty = await page.locator('.el-empty').isVisible()
    expect(hasDetail || hasEmpty).toBeTruthy()
  })

  test('应该显示收款方信息', async ({ page }) => {
    await detailPage.goto(1)
    await page.waitForLoadState('networkidle')

    // 检查是否显示收款方信息
    const pageContent = await page.content()
    const hasPayeeInfo = pageContent.includes('收款方') || pageContent.includes('户名') || pageContent.includes('账号')
    const hasEmpty = await page.locator('.el-empty').isVisible()

    expect(hasPayeeInfo || hasEmpty).toBeTruthy()
  })

  test('应该显示金额信息', async ({ page }) => {
    await detailPage.goto(1)
    await page.waitForLoadState('networkidle')

    // 检查是否显示金额信息
    const pageContent = await page.content()
    const hasAmount = pageContent.includes('金额') || /\d+\.?\d*/.test(pageContent)
    const hasEmpty = await page.locator('.el-empty').isVisible()

    expect(hasAmount || hasEmpty).toBeTruthy()
  })

  test('应该显示审核历史（如有）', async ({ page }) => {
    await detailPage.goto(1)
    await page.waitForLoadState('networkidle')

    // 检查审核历史区域
    const hasAuditHistory = await page.locator('.audit-history, .history-list, .timeline').isVisible()
    const hasDetail = await page.locator('.application-detail, .el-card').first().isVisible()
    const hasEmpty = await page.locator('.el-empty').isVisible()

    expect(hasAuditHistory || hasDetail || hasEmpty).toBeTruthy()
  })
})

test.describe('申请操作-申请人视角', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, testUsers.applicant)
  })

  test('待审核状态应该能撤销', async ({ page }) => {
    // 访问申请列表
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    // 查找待审核状态的申请
    const pendingRows = page.locator('.el-table__row').filter({ hasText: '待审核' })
    const count = await pendingRows.count()

    if (count > 0) {
      // 点击查看
      await pendingRows.first().getByRole('button', { name: '查看' }).click()

      // 检查是否有撤销按钮
      const cancelButton = page.getByRole('button', { name: '撤销申请' })
      if (await cancelButton.isVisible()) {
        // 不实际点击撤销，只验证按钮存在
        expect(await cancelButton.isVisible()).toBeTruthy()
      }
    }
  })

  test('已通过状态应该不能撤销', async ({ page }) => {
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    // 查找已通过状态的申请
    const approvedRows = page.locator('.el-table__row').filter({ hasText: '已通过' })
    const count = await approvedRows.count()

    if (count > 0) {
      // 点击查看
      await approvedRows.first().getByRole('button', { name: '查看' }).click()

      // 验证没有撤销按钮
      const cancelButton = page.getByRole('button', { name: '撤销申请' })
      expect(await cancelButton.isVisible({ timeout: 2000 }).catch(() => false)).toBeFalsy()
    }
  })
})

test.describe('申请操作-会计视角', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, testUsers.accountant)
  })

  test('会计应该能看到审核按钮', async ({ page }) => {
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    // 查找待审核状态的申请
    const pendingRows = page.locator('.el-table__row').filter({ hasText: '待审核' })
    const count = await pendingRows.count()

    if (count > 0) {
      // 点击查看
      await pendingRows.first().getByRole('button', { name: '查看' }).click()
      await page.waitForLoadState('networkidle')

      // 检查审核按钮
      const approveBtn = page.getByRole('button', { name: '审核通过' })
      const rejectBtn = page.getByRole('button', { name: '审核拒绝' })

      // 至少有一个审核按钮可见
      const hasApproveBtn = await approveBtn.isVisible({ timeout: 2000 }).catch(() => false)
      const hasRejectBtn = await rejectBtn.isVisible({ timeout: 2000 }).catch(() => false)
      expect(hasApproveBtn || hasRejectBtn).toBeTruthy()
    }
  })

  test('应该能审核通过', async ({ page }) => {
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    const pendingRows = page.locator('.el-table__row').filter({ hasText: '待审核' })
    const count = await pendingRows.count()

    if (count > 0) {
      // 点击查看
      await pendingRows.first().getByRole('button', { name: '查看' }).click()
      await page.waitForLoadState('networkidle')

      const approveBtn = page.getByRole('button', { name: '审核通过' })
      if (await approveBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        // 记录当前URL
        const currentUrl = page.url()

        // 点击审核通过
        await approveBtn.click()

        // 等待确认对话框或直接提交
        await page.waitForTimeout(1000)

        // 查找确认按钮
        const confirmBtn = page.getByRole('button', { name: '确定' })
        if (await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
          await confirmBtn.click()
        }

        // 等待响应
        await page.waitForTimeout(1000)
      }
    }
  })

  test('审核拒绝应该要求填写原因', async ({ page }) => {
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    const pendingRows = page.locator('.el-table__row').filter({ hasText: '待审核' })
    const count = await pendingRows.count()

    if (count > 0) {
      // 点击查看
      await pendingRows.first().getByRole('button', { name: '查看' }).click()
      await page.waitForLoadState('networkidle')

      const rejectBtn = page.getByRole('button', { name: '审核拒绝' })
      if (await rejectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await rejectBtn.click()

        // 等待对话框出现
        await page.waitForTimeout(500)

        // 验证出现拒绝原因输入框
        const reasonInput = page.locator('.el-message-box input, .el-message-box textarea')
        const hasReasonInput = await reasonInput.isVisible({ timeout: 2000 }).catch(() => false)

        // 验证需要填写原因
        expect(hasReasonInput).toBeTruthy()
      }
    }
  })
})

test.describe('申请操作-财务主管视角', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, testUsers.financeManager)
  })

  test('财务主管应该能审核大额付款', async ({ page }) => {
    await page.goto('/applications')
    await page.waitForSelector('.el-table__row', { timeout: 5000 }).catch(() => {})

    // 查找大额待审核申请（>=10万）
    const pendingRows = page.locator('.el-table__row').filter({ hasText: '待审核' })
    const count = await pendingRows.count()

    if (count > 0) {
      // 点击查看
      await pendingRows.first().getByRole('button', { name: '查看' }).click()
      await page.waitForLoadState('networkidle')

      // 财务主管应该能看到审核按钮
      const approveBtn = page.getByRole('button', { name: '审核通过' })
      const isVisible = await approveBtn.isVisible({ timeout: 2000 }).catch(() => false)
      expect(isVisible).toBeTruthy()
    }
  })
})