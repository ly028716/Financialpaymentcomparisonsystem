/**
 * 测试认证 Fixtures
 * 提供统一的认证方法
 */
import { Page } from '@playwright/test'

export interface TestUser {
  id: number
  username: string
  name: string
  role: 'applicant' | 'accountant' | 'cashier' | 'finance_manager' | 'admin'
  department: string
}

// 预定义测试用户
export const testUsers = {
  applicant: {
    id: 1,
    username: 'applicant',
    name: '申请人张三',
    role: 'applicant' as const,
    department: '技术部'
  },
  accountant: {
    id: 2,
    username: 'accountant',
    name: '会计李四',
    role: 'accountant' as const,
    department: '财务部'
  },
  cashier: {
    id: 3,
    username: 'cashier',
    name: '出纳王五',
    role: 'cashier' as const,
    department: '财务部'
  },
  financeManager: {
    id: 4,
    username: 'manager',
    name: '财务主管赵六',
    role: 'finance_manager' as const,
    department: '财务部'
  },
  admin: {
    id: 5,
    username: 'admin',
    name: '系统管理员',
    role: 'admin' as const,
    department: 'IT部'
  }
}

/**
 * 模拟用户登录 - 设置localStorage并等待状态稳定
 */
export async function loginAs(page: Page, user: TestUser) {
  // 先确保在登录页或空白页设置token
  await page.goto('/login')

  // 设置localStorage
  await page.evaluate((u) => {
    localStorage.setItem('token', 'test-token-' + u.id)
    localStorage.setItem('user', JSON.stringify(u))
  }, user)

  // 等待localStorage设置完成
  await page.waitForTimeout(100)
}

/**
 * 清除登录状态
 */
export async function logout(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  })
}

/**
 * 检查是否已登录
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  return await page.evaluate(() => {
    return !!localStorage.getItem('token')
  })
}

/**
 * 验证登录状态是否有效
 */
export async function ensureLoggedIn(page: Page, user: TestUser) {
  const loggedIn = await isLoggedIn(page)
  if (!loggedIn) {
    await loginAs(page, user)
  }
}