// OCR识别结果类型定义
export interface OcrResult {
  payee_name: string
  payee_account: string
  amount: string
  payment_date: string
  bank_name?: string
  transaction_id?: string
}

// OCR上传状态
export type OcrUploadStatus = 'idle' | 'uploading' | 'success' | 'error'

// OCR组件Props
export interface OcrUploaderProps {
  modelValue?: OcrResult | null
  disabled?: boolean
}

// OCR组件Emits
export interface OcrUploaderEmits {
  (e: 'update:modelValue', value: OcrResult | null): void
  (e: 'success', result: OcrResult): void
  (e: 'error', error: Error): void
}
