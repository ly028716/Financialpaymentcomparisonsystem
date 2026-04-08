<template>
  <div class="ocr-uploader">
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      :disabled="disabled"
      @change="handleFileChange"
    />

    <el-button
      type="primary"
      :disabled="disabled || status === 'uploading'"
      :loading="status === 'uploading'"
      @click="triggerFileInput"
    >
      <el-icon v-if="status !== 'uploading'"><Upload /></el-icon>
      上传银行回单
    </el-button>

    <div v-if="imagePreview" class="image-preview">
      <el-image :src="imagePreview" fit="contain" style="max-width: 400px; max-height: 300px" />
    </div>

    <div v-if="status === 'uploading'" class="loading-spinner">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>识别中...</span>
    </div>

    <div v-if="errorMessage" class="error-message">
      <el-alert type="error" :title="errorMessage" :closable="false" />
    </div>

    <div v-if="ocrResult && status === 'success'" class="ocr-result">
      <el-card>
        <template #header>
          <span>识别结果</span>
        </template>
        <el-form label-width="120px">
          <el-form-item label="收款人名称">
            <el-input v-model="editableResult.payee_name" />
          </el-form-item>
          <el-form-item label="收款账号">
            <el-input v-model="editableResult.payee_account" />
          </el-form-item>
          <el-form-item label="付款金额">
            <el-input v-model="editableResult.amount" />
          </el-form-item>
          <el-form-item label="付款日期">
            <el-input v-model="editableResult.payment_date" />
          </el-form-item>
          <el-form-item label="银行名称">
            <el-input v-model="editableResult.bank_name" />
          </el-form-item>
          <el-form-item label="交易流水号">
            <el-input v-model="editableResult.transaction_id" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="confirmResult">确认</el-button>
            <el-button @click="resetUpload">重新上传</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Loading } from '@element-plus/icons-vue'
import { paymentApi } from '@/api'
import type { OcrResult, OcrUploadStatus } from '@/types/ocr'

interface Props {
  modelValue?: OcrResult | null
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: OcrResult | null): void
  (e: 'success', result: OcrResult): void
  (e: 'error', error: Error): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  disabled: false
})

const emit = defineEmits<Emits>()

const fileInputRef = ref<HTMLInputElement>()
const imagePreview = ref<string>('')
const status = ref<OcrUploadStatus>('idle')
const errorMessage = ref<string>('')
const ocrResult = ref<OcrResult | null>(null)
const EMPTY_OCR_RESULT: OcrResult = {
  payee_name: '',
  payee_account: '',
  amount: '',
  payment_date: '',
  bank_name: '',
  transaction_id: ''
}

const editableResult = reactive<OcrResult>({ ...EMPTY_OCR_RESULT })

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      ocrResult.value = newValue
      Object.assign(editableResult, newValue)
    }
  },
  { immediate: true }
)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

const validateFile = (file: File): boolean => {
  if (!file.type.startsWith('image/')) {
    const error = new Error('只支持图片文件')
    errorMessage.value = error.message
    ElMessage.error(error.message)
    emit('error', error)
    return false
  }

  if (file.size > MAX_FILE_SIZE) {
    const error = new Error('文件大小不能超过5MB')
    errorMessage.value = error.message
    ElMessage.error(error.message)
    emit('error', error)
    return false
  }

  return true
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  errorMessage.value = ''

  if (!validateFile(file)) {
    target.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  await performOcr(file)

  target.value = ''
}

const performOcr = async (file: File) => {
  status.value = 'uploading'
  errorMessage.value = ''

  try {
    const response = await paymentApi.ocr(file)
    ocrResult.value = response.data
    Object.assign(editableResult, response.data)
    status.value = 'success'
    emit('update:modelValue', response.data)
    emit('success', response.data)
    ElMessage.success('识别成功')
  } catch (error: any) {
    status.value = 'error'
    errorMessage.value = error.message || 'OCR识别失败'
    ElMessage.error(errorMessage.value)
    emit('error', error)
  }
}

const confirmResult = () => {
  const result = { ...editableResult }
  ocrResult.value = result
  emit('update:modelValue', result)
  emit('success', result)
  ElMessage.success('已确认识别结果')
}

const resetUpload = () => {
  imagePreview.value = ''
  status.value = 'idle'
  errorMessage.value = ''
  ocrResult.value = null
  Object.assign(editableResult, EMPTY_OCR_RESULT)
  emit('update:modelValue', null)
}
</script>

<style scoped>
.ocr-uploader {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-preview {
  margin-top: 16px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-color-primary);
}

.error-message {
  margin-top: 8px;
}

.ocr-result {
  margin-top: 16px;
}
</style>
