/**
 * 银行卡号工具函数
 */

/**
 * Luhn 算法校验银行卡号
 * @param account 银行卡号
 * @returns 是否有效
 */
export function luhnCheck(account: string): boolean {
  if (!account || !/^\d+$/.test(account)) {
    return false
  }

  const digits = account.split('').map(d => parseInt(d))
  const reversed = [...digits].reverse()
  const oddDigits = reversed.filter((_, i) => i % 2 === 0)
  const evenDigits = reversed.filter((_, i) => i % 2 === 1)

  let total = oddDigits.reduce((sum, d) => sum + d, 0)

  for (const d of evenDigits) {
    let doubled = d * 2
    if (doubled > 9) {
      doubled = doubled - 9
    }
    total += doubled
  }

  return total % 10 === 0
}

/**
 * 计算 Luhn 校验位
 * @param partialAccount 不含校验位的账号
 * @returns 校验位（0-9）
 */
export function calculateLuhnChecksum(partialAccount: string): number {
  const digits = partialAccount.split('').map(d => parseInt(d))
  digits.push(0) // 添加临时校验位

  const reversed = [...digits].reverse()
  const oddDigits = reversed.filter((_, i) => i % 2 === 0)
  const evenDigits = reversed.filter((_, i) => i % 2 === 1)

  let total = oddDigits.reduce((sum, d) => sum + d, 0)

  for (const d of evenDigits) {
    let doubled = d * 2
    if (doubled > 9) {
      doubled = doubled - 9
    }
    total += doubled
  }

  const checksum = (10 - (total % 10)) % 10
  return checksum
}

/**
 * 生成测试用的有效银行卡号
 * @param bankPrefix 银行卡号前缀（可选）
 * @returns 有效的银行卡号
 */
export function generateTestBankAccount(bankPrefix?: string): string {
  // 常见银行卡号前缀
  const prefixes = [
    '622202', // 工商银行
    '622848', // 农业银行
    '622700', // 建设银行
    '621661', // 中国银行
    '622588', // 招商银行
  ]

  const prefix = bankPrefix || prefixes[Math.floor(Math.random() * prefixes.length)]

  // 生成随机的中间数字（保证总长度为16位）
  const middleLength = 16 - prefix.length - 1 // 减去前缀和校验位
  let middle = ''
  for (let i = 0; i < middleLength; i++) {
    middle += Math.floor(Math.random() * 10)
  }

  const partial = prefix + middle
  const checksum = calculateLuhnChecksum(partial)

  return partial + checksum
}

/**
 * 账号脱敏显示
 * @param account 银行卡号
 * @param showFirst 显示前几位
 * @param showLast 显示后几位
 * @returns 脱敏后的账号
 */
export function maskAccount(account: string, showFirst = 4, showLast = 4): string {
  if (!account) {
    return ''
  }

  const cleaned = account.replace(/\s/g, '')

  if (cleaned.length <= showFirst + showLast) {
    return cleaned
  }

  const first = cleaned.slice(0, showFirst)
  const last = cleaned.slice(-showLast)
  const middle = '*'.repeat(cleaned.length - showFirst - showLast)

  return `${first}${middle}${last}`
}

/**
 * 格式化账号显示（按4位分组）
 * @param account 银行卡号
 * @returns 格式化后的账号
 */
export function formatAccountDisplay(account: string): string {
  if (!account) {
    return ''
  }

  const cleaned = account.replace(/\s/g, '')
  const groups: string[] = []

  for (let i = 0; i < cleaned.length; i += 4) {
    groups.push(cleaned.slice(i, i + 4))
  }

  return groups.join(' ')
}

/**
 * 测试用的有效银行卡号列表
 */
export const TEST_BANK_ACCOUNTS = [
  '6222021234567894', // 工商银行
  '6228481234567893', // 农业银行
  '6217001234567896', // 建设银行
  '6216611234567899', // 中国银行
  '6225881234567892', // 招商银行
]
