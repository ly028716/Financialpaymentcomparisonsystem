/**
 * 仪表盘页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class DashboardPage {
  readonly page: Page
  readonly statCards: Locator
  readonly quickCreateButton: Locator
  readonly recentApplications: Locator
  readonly chartContainer: Locator

  constructor(page: Page) {
    this.page = page
    this.statCards = page.locator('.stat-card')
    this.quickCreateButton = page.getByRole('button', { name: '创建付款申请' })
    this.recentApplications = page.locator('.recent-applications')
    this.chartContainer = page.locator('.chart-container')
  }

  async goto() {
    await this.page.goto('/dashboard')
    await this.page.waitForLoadState('networkidle')
  }

  async getStatCardCount(): Promise<number> {
    return await this.statCards.count()
  }

  async clickQuickCreate() {
    await this.quickCreateButton.click()
    await this.page.waitForURL('**/applications/create')
  }

  async expectDashboardVisible() {
    await expect(this.page.locator('.dashboard')).toBeVisible()
  }
}