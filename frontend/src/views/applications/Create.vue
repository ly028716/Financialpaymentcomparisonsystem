<template>
  <div class="application-create">
    <el-card>
      <template #header>
        <span>创建付款申请</span>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="create-form"
      >
        <el-form-item label="收款方户名" prop="payee_name">
          <el-input
            v-model="form.payee_name"
            placeholder="请输入收款方户名"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="收款方账号" prop="payee_account">
          <el-input
            v-model="form.payee_account"
            placeholder="请输入收款方账号（10-30位数字）"
            maxlength="30"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="开户行" prop="payee_bank">
          <el-input
            v-model="form.payee_bank"
            placeholder="请输入开户行"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="付款金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :precision="2"
            :min="0.01"
            :max="999999999.99"
            :controls="false"
            class="amount-input"
          />
        </el-form-item>

        <el-form-item label="付款用途" prop="purpose">
          <el-input
            v-model="form.purpose"
            type="textarea"
            :rows="3"
            placeholder="请输入付款用途"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="是否紧急">
          <el-switch v-model="form.urgent" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            提交申请
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { applicationApi } from '@/api'

// 定义表单数据类型
interface ApplicationForm {
  payee_name: string
  payee_account: string
  payee_bank: string
  amount: number
  purpose: string
  urgent: boolean
  remark: string
}

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive<ApplicationForm>({
  payee_name: '',
  payee_account: '',
  payee_bank: '',
  amount: 0,
  purpose: '',
  urgent: false,
  remark: ''
})

// 自定义验证规则
const validatePayeeName = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入收款方户名'))
  } else if (value.length < 2 || value.length > 200) {
    callback(new Error('户名长度为 2-200 个字符'))
  } else if (!/^[\u4e00-\u9fa5a-zA-Z0-9()（）\s]+$/.test(value)) {
    callback(new Error('户名格式不正确，仅支持中英文、数字和括号'))
  } else {
    callback()
  }
}

const validatePayeeAccount = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入收款方账号'))
  } else if (!/^[0-9]{10,30}$/.test(value)) {
    callback(new Error('账号格式不正确（10-30位数字）'))
  } else {
    callback()
  }
}

const validatePayeeBank = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入开户行'))
  } else if (value.length < 2 || value.length > 200) {
    callback(new Error('开户行长度为 2-200 个字符'))
  } else {
    callback()
  }
}

const validateAmount = (_rule: any, value: number, callback: any) => {
  if (!value || value <= 0) {
    callback(new Error('请输入有效的付款金额'))
  } else if (value < 0.01) {
    callback(new Error('金额必须大于 0.01'))
  } else if (value > 999999999.99) {
    callback(new Error('金额不能超过 999,999,999.99'))
  } else {
    callback()
  }
}

const validatePurpose = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入付款用途'))
  } else if (value.length < 2 || value.length > 500) {
    callback(new Error('付款用途长度为 2-500 个字符'))
  } else {
    callback()
  }
}

const rules: FormRules<ApplicationForm> = {
  payee_name: [{ validator: validatePayeeName, trigger: 'blur' }],
  payee_account: [{ validator: validatePayeeAccount, trigger: 'blur' }],
  payee_bank: [{ validator: validatePayeeBank, trigger: 'blur' }],
  amount: [{ validator: validateAmount, trigger: 'blur' }],
  purpose: [{ validator: validatePurpose, trigger: 'blur' }]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }

  loading.value = true
  try {
    await applicationApi.create(form)
    ElMessage.success('申请提交成功')
    router.push('/applications')
  } catch (error: any) {
    // 仅在开发环境输出错误信息
    if (import.meta.env.DEV) {
      console.error('提交失败', error)
    }

    // 显示具体错误信息
    const message = error?.response?.data?.message || '提交失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-form {
  max-width: 600px;
}

.amount-input {
  width: 100%;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .create-form {
    max-width: 100%;
  }
}
</style>