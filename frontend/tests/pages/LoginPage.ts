/**
 * 登录页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class LoginPage {
  readonly page: Page
  readonly usernameInput: Locator
  readonly passwordInput: Locator
  readonly loginButton: Locator
  readonly errorMessage: Locator

  constructor(page: Page) {
    this.page = page
    this.usernameInput = page.locator('[data-testid="username-input"]')
    this.passwordInput = page.locator('[data-testid="password-input"]')
    this.loginButton = page.locator('[data-testid="login-btn"]')
    this.errorMessage = page.locator('.el-message--error')
  }

  async goto() {
    await this.page.goto('/login')
    await this.page.waitForLoadState('networkidle')
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username)
    await this.passwordInput.fill(password)
    await this.loginButton.click()
  }

  async expectLoginSuccess() {
    await this.page.waitForURL('**/dashboard', { timeout: 10000 })
  }

  async expectLoginError() {
    await expect(this.errorMessage.first()).toBeVisible({ timeout: 5000 })
  }

  async expectValidationError() {
    await expect(this.page.locator('.el-form-item__error').first()).toBeVisible()
  }
}