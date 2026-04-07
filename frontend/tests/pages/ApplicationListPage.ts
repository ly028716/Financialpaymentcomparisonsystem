/**
 * 付款申请列表页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class ApplicationListPage {
  readonly page: Page
  readonly table: Locator
  readonly tableRows: Locator
  readonly createButton: Locator
  readonly statusFilter: Locator
  readonly searchInput: Locator

  constructor(page: Page) {
    this.page = page
    this.table = page.locator('.application-list .el-table')
    this.tableRows = page.locator('.el-table__row')
    this.createButton = page.getByRole('button', { name: '创建申请' })
    this.statusFilter = page.locator('.el-select').first()
    this.searchInput = page.locator('[placeholder*="搜索"]')
  }

  async goto() {
    await this.page.goto('/applications')
    await this.page.waitForLoadState('networkidle')
  }

  async clickCreate() {
    await this.createButton.click()
    await this.page.waitForURL('**/applications/create')
  }

  async filterByStatus(status: string) {
    await this.statusFilter.click()
    await this.page.getByText(status).click()
    await this.page.waitForTimeout(500)
  }

  async getRowCount(): Promise<number> {
    return await this.tableRows.count()
  }

  async viewFirstApplication() {
    const viewBtn = this.page.getByRole('button', { name: '查看' }).first()
    if (await viewBtn.isVisible()) {
      await viewBtn.click()
      await this.page.waitForURL(/\/applications\/\d+/)
    }
  }

  async clickApproveFirst() {
    const approveBtn = this.page.getByRole('button', { name: '审核通过' }).first()
    if (await approveBtn.isVisible()) {
      await approveBtn.click()
    }
  }

  async expectTableVisible() {
    await expect(this.table).toBeVisible()
  }
}