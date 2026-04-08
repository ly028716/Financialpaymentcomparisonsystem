<template>
  <div class="payment-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>出纳付款</span>
          <el-button type="primary" @click="showOcrDialog = true">
            上传银行回单
          </el-button>
        </div>
      </template>
      <el-empty description="付款记录列表（待开发）" />
    </el-card>

    <el-dialog
      v-model="showOcrDialog"
      title="上传银行回单"
      width="600px"
      @close="handleDialogClose"
    >
      <ocr-uploader
        v-model="ocrResult"
        @success="handleOcrSuccess"
        @error="handleOcrError"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import OcrUploader from '@/components/OcrUploader.vue'
import type { OcrResult } from '@/types/ocr'

const showOcrDialog = ref(false)
const ocrResult = ref<OcrResult | null>(null)

const handleOcrSuccess = (result: OcrResult) => {
  ElMessage.success('识别成功，可以继续编辑或确认')
  console.log('OCR识别结果:', result)
}

const handleOcrError = (error: Error) => {
  console.error('OCR识别失败:', error)
}

const handleDialogClose = () => {
  ocrResult.value = null
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
