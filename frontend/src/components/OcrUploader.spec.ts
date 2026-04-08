import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import OcrUploader from './OcrUploader.vue'
import { paymentApi } from '@/api'
import type { OcrResult } from '@/types/ocr'

vi.mock('@/api', () => ({
  paymentApi: {
    ocr: vi.fn()
  }
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn()
  },
  ElButton: { name: 'ElButton', template: '<button><slot /></button>' },
  ElIcon: { name: 'ElIcon', template: '<i><slot /></i>' },
  ElImage: { name: 'ElImage', template: '<img />' },
  ElAlert: { name: 'ElAlert', template: '<div class="el-alert"><slot /></div>' },
  ElCard: { name: 'ElCard', template: '<div class="el-card"><slot name="header" /><slot /></div>' },
  ElForm: { name: 'ElForm', template: '<form><slot /></form>' },
  ElFormItem: { name: 'ElFormItem', template: '<div class="el-form-item"><slot /></div>' },
  ElInput: { name: 'ElInput', template: '<input />' }
}))

vi.mock('@element-plus/icons-vue', () => ({
  Upload: { name: 'Upload', template: '<span>Upload</span>' },
  Loading: { name: 'Loading', template: '<span>Loading</span>' }
}))

describe('OcrUploader', () => {
  const mockOcrResult: OcrResult = {
    payee_name: '测试收款人',
    payee_account: '6222021234567890123',
    amount: '10000.00',
    payment_date: '2026-04-08',
    bank_name: '中国工商银行',
    transaction_id: 'TXN123456789'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该渲染上传按钮', () => {
      const wrapper = mount(OcrUploader)
      expect(wrapper.find('.ocr-uploader').exists()).toBe(true)
      expect(wrapper.text()).toContain('上传银行回单')
    })

    it('应该接受disabled属性', () => {
      const wrapper = mount(OcrUploader, {
        props: { disabled: true }
      })
      const input = wrapper.find('input[type="file"]')
      expect(input.attributes('disabled')).toBeDefined()
    })
  })

  describe('文件上传', () => {
    it('应该接受图片文件', async () => {
      vi.mocked(paymentApi.ocr).mockResolvedValue({
        code: 200,
        message: '识别成功',
        data: mockOcrResult
      })

      const wrapper = mount(OcrUploader)
      const file = new File(['image'], 'receipt.jpg', { type: 'image/jpeg' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')

      // 等待FileReader和OCR完成
      await new Promise(resolve => setTimeout(resolve, 50))
      await nextTick()

      expect(wrapper.vm.imagePreview).toBeTruthy()
    })

    it('应该拒绝非图片文件', async () => {
      const wrapper = mount(OcrUploader)
      const file = new File(['pdf'], 'doc.pdf', { type: 'application/pdf' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')
      await nextTick()

      expect(wrapper.emitted('error')).toBeTruthy()
    })
  })

  describe('OCR识别', () => {
    it('上传成功后应该自动调用OCR API', async () => {
      vi.mocked(paymentApi.ocr).mockResolvedValue({
        code: 200,
        message: '识别成功',
        data: mockOcrResult
      })

      const wrapper = mount(OcrUploader)
      const file = new File(['image'], 'receipt.jpg', { type: 'image/jpeg' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')
      await nextTick()
      await nextTick()

      expect(paymentApi.ocr).toHaveBeenCalledWith(file)
    })

    it('识别成功后应该显示结果', async () => {
      vi.mocked(paymentApi.ocr).mockResolvedValue({
        code: 200,
        message: '识别成功',
        data: mockOcrResult
      })

      const wrapper = mount(OcrUploader)
      const file = new File(['image'], 'receipt.jpg', { type: 'image/jpeg' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')
      await nextTick()
      await nextTick()
      await nextTick()

      expect(wrapper.find('.ocr-result').exists()).toBe(true)
      const resultHtml = wrapper.html()
      expect(resultHtml).toContain(mockOcrResult.payee_name)
    })

    it('识别失败应该显示错误', async () => {
      vi.mocked(paymentApi.ocr).mockRejectedValue(new Error('OCR失败'))

      const wrapper = mount(OcrUploader)
      const file = new File(['image'], 'receipt.jpg', { type: 'image/jpeg' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')
      await nextTick()
      await nextTick()

      expect(wrapper.emitted('error')).toBeTruthy()
    })
  })

  describe('v-model绑定', () => {
    it('应该支持v-model双向绑定', async () => {
      vi.mocked(paymentApi.ocr).mockResolvedValue({
        code: 200,
        message: '识别成功',
        data: mockOcrResult
      })

      const wrapper = mount(OcrUploader, {
        props: {
          modelValue: null,
          'onUpdate:modelValue': (value: OcrResult | null) =>
            wrapper.setProps({ modelValue: value })
        }
      })

      const file = new File(['image'], 'receipt.jpg', { type: 'image/jpeg' })
      const input = wrapper.find('input[type="file"]')

      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false
      })

      await input.trigger('change')
      await nextTick()
      await nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      const emitted = wrapper.emitted('update:modelValue') as any[]
      expect(emitted[0][0]).toEqual(mockOcrResult)
    })
  })
})
