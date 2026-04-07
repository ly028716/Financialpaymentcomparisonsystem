/**
 * 申请详情页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class ApplicationDetailPage {
  readonly page: Page
  readonly applicationNo: Locator
  readonly statusTag: Locator
  readonly approveButton: Locator
  readonly rejectButton: Locator
  readonly editButton: Locator
  readonly cancelButton: Locator
  readonly auditHistory: Locator

  constructor(page: Page) {
    this.page = page
    this.applicationNo = page.locator('.application-detail .application-no')
    this.statusTag = page.locator('.application-detail .el-tag')
    this.approveButton = page.getByRole('button', { name: '审核通过' })
    this.rejectButton = page.getByRole('button', { name: '审核拒绝' })
    this.editButton = page.getByRole('button', { name: '编辑' })
    this.cancelButton = page.getByRole('button', { name: '撤销申请' })
    this.auditHistory = page.locator('.audit-history')
  }

  async goto(id: number) {
    await this.page.goto(`/applications/${id}`)
    await this.page.waitForLoadState('networkidle')
  }

  async approve(note?: string) {
    if (await this.approveButton.isVisible()) {
      await this.approveButton.click()
      if (note) {
        await this.page.locator('textarea[placeholder*="审核备注"]').fill(note)
      }
      await this.page.getByRole('button', { name: '确认' }).click()
    }
  }

  async reject(reason: string) {
    if (await this.rejectButton.isVisible()) {
      await this.rejectButton.click()
      await this.page.locator('textarea[placeholder*="拒绝原因"]').fill(reason)
      await this.page.getByRole('button', { name: '确认' }).click()
    }
  }

  async cancelApplication() {
    if (await this.cancelButton.isVisible()) {
      await this.cancelButton.click()
      await this.page.getByRole('button', { name: '确认' }).click()
    }
  }

  async getStatus(): Promise<string> {
    return await this.statusTag.textContent() || ''
  }

  async expectDetailVisible() {
    await expect(this.page.locator('.application-detail')).toBeVisible()
  }
}