/**
 * 付款列表页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class PaymentListPage {
  readonly page: Page
  readonly table: Locator
  readonly tableRows: Locator
  readonly recordPaymentButton: Locator
  readonly ocrButton: Locator

  constructor(page: Page) {
    this.page = page
    this.table = page.locator('.payment-list .el-table')
    this.tableRows = page.locator('.el-table__row')
    this.recordPaymentButton = page.getByRole('button', { name: '记录付款' })
    this.ocrButton = page.getByRole('button', { name: 'OCR识别' })
  }

  async goto() {
    await this.page.goto('/payments')
    await this.page.waitForLoadState('networkidle')
  }

  async getRowCount(): Promise<number> {
    return await this.tableRows.count()
  }

  async recordPaymentForFirst() {
    const recordBtn = this.page.getByRole('button', { name: '记录付款' }).first()
    if (await recordBtn.isVisible()) {
      await recordBtn.click()
    }
  }

  async expectTableVisible() {
    await expect(this.table).toBeVisible()
  }
}