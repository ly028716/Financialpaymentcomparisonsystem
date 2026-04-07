/**
 * 创建付款申请页 Page Object
 */
import { Page, Locator, expect } from '@playwright/test'

export class ApplicationCreatePage {
  readonly page: Page
  readonly payeeNameInput: Locator
  readonly payeeAccountInput: Locator
  readonly payeeBankInput: Locator
  readonly amountInput: Locator
  readonly purposeInput: Locator
  readonly remarkInput: Locator
  readonly submitButton: Locator
  readonly cancelButton: Locator

  constructor(page: Page) {
    this.page = page
    this.payeeNameInput = page.locator('input[placeholder*="收款方户名"]')
    this.payeeAccountInput = page.locator('input[placeholder*="收款方账号"]')
    this.payeeBankInput = page.locator('input[placeholder*="开户行"]')
    this.amountInput = page.locator('.el-input-number input, .amount-input input').first()
    this.purposeInput = page.locator('textarea[placeholder*="付款用途"]')
    this.remarkInput = page.locator('textarea[placeholder*="备注"]')
    this.submitButton = page.getByRole('button', { name: '提交申请' })
    this.cancelButton = page.getByRole('button', { name: '取消' })
  }

  async goto() {
    await this.page.goto('/applications/create')
    await this.page.waitForLoadState('networkidle')
  }

  async fillForm(data: {
    payeeName: string
    payeeAccount: string
    payeeBank: string
    amount: string
    purpose: string
    remark?: string
  }) {
    await this.payeeNameInput.fill(data.payeeName)
    await this.payeeAccountInput.fill(data.payeeAccount)
    await this.payeeBankInput.fill(data.payeeBank)

    // 金额输入框可能需要特殊处理
    const amountField = this.page.locator('.el-input-number input').first()
    await amountField.click()
    await amountField.fill(data.amount)

    await this.purposeInput.fill(data.purpose)
    if (data.remark) {
      await this.remarkInput.fill(data.remark)
    }
  }

  async submit() {
    await this.submitButton.click()
  }

  async cancel() {
    await this.cancelButton.click()
  }

  async expectValidationError() {
    await expect(this.page.locator('.el-form-item__error').first()).toBeVisible()
  }

  async expectSubmitSuccess() {
    // 等待跳转或成功消息
    await this.page.waitForURL('**/applications', { timeout: 10000 }).catch(async () => {
      // 如果没有跳转，检查是否有成功消息
      const successMessage = this.page.locator('.el-message--success')
      await expect(successMessage).toBeVisible({ timeout: 5000 })
    })
  }
}