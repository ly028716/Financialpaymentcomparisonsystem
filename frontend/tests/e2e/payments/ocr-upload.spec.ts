import { test, expect } from '@playwright/test'

test.describe('OCR上传功能', () => {
  test.beforeEach(async ({ page }) => {
    // 假设需要登录
    await page.goto('/login')
    await page.fill('input[type="text"]', 'cashier')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')

    // 导航到付款页面
    await page.goto('/payments')
  })

  test('应该显示上传银行回单按钮', async ({ page }) => {
    await expect(page.getByText('上传银行回单')).toBeVisible()
  })

  test('点击按钮应该打开OCR上传对话框', async ({ page }) => {
    await page.getByText('上传银行回单').click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByText('上传银行回单', { exact: false })).toBeVisible()
  })

  test('应该能够上传图片并显示预览', async ({ page }) => {
    await page.getByText('上传银行回单').click()

    // 模拟文件上传
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'receipt.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from('fake image content')
    })

    // 等待预览显示
    await expect(page.locator('.image-preview')).toBeVisible({ timeout: 5000 })
  })
})
