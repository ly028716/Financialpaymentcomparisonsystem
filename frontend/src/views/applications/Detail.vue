<template>
  <div class="application-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>申请详情</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="申请单号">
          {{ detail?.application_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag v-if="detail?.status" :type="getStatusType(detail.status)">
            {{ getStatusText(detail.status) }}
          </el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="申请部门">
          {{ detail?.department || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ detail?.applicant || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="收款方户名">
          {{ detail?.payee_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="收款方账号">
          {{ detail?.payee_account || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="开户行">
          {{ detail?.payee_bank || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="付款金额">
          <span class="amount">¥{{ formatAmount(detail?.amount) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="付款用途" :span="2">
          {{ detail?.purpose || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ detail?.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 审核操作 -->
      <div v-if="detail?.status === 'pending'" class="action-buttons">
        <el-button type="success" :loading="approving" @click="handleApprove">
          审核通过
        </el-button>
        <el-button type="danger" :loading="rejecting" @click="handleReject">
          审核拒绝
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { applicationApi } from '@/api'

// 定义申请详情类型
interface ApplicationDetail {
  id: number
  application_no: string
  department: string
  applicant: string
  payee_name: string
  payee_account: string
  payee_bank: string
  amount: number
  purpose: string
  status: string
  urgent: boolean
  remark: string
  created_at: string
  updated_at: string
}

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const approving = ref(false)
const rejecting = ref(false)
const detail = ref<ApplicationDetail | null>(null)

const fetchDetail = async () => {
  const id = Number(route.params.id)

  if (!id || isNaN(id)) {
    ElMessage.error('无效的申请ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const res = await applicationApi.getDetail(id)
    if (res?.data) {
      detail.value = res.data
    }
  } catch (error: any) {
    // 仅在开发环境输出错误信息
    if (import.meta.env.DEV) {
      console.error('获取详情失败', error)
    }

    const message = error?.response?.data?.message || '获取详情失败，请稍后重试'
    ElMessage.error(message)

    // 如果是404错误，返回列表页
    if (error?.response?.status === 404) {
      setTimeout(() => router.back(), 1500)
    }
  } finally {
    loading.value = false
  }
}

const handleApprove = async () => {
  if (!detail.value?.id) {
    ElMessage.error('申请信息不完整')
    return
  }

  try {
    await ElMessageBox.confirm('确定审核通过吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
  } catch {
    return
  }

  approving.value = true
  try {
    await applicationApi.approve(detail.value.id, '审核通过')
    ElMessage.success('审核成功')
    await fetchDetail()
  } catch (error: any) {
    if (import.meta.env.DEV) {
      console.error('审核失败', error)
    }

    const message = error?.response?.data?.message || '审核失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    approving.value = false
  }
}

const handleReject = async () => {
  if (!detail.value?.id) {
    ElMessage.error('申请信息不完整')
    return
  }

  let reason = ''
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '审核拒绝', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请输入拒绝原因'
    })
    reason = value
  } catch {
    return
  }

  rejecting.value = true
  try {
    await applicationApi.reject(detail.value.id, reason)
    ElMessage.success('已拒绝')
    await fetchDetail()
  } catch (error: any) {
    if (import.meta.env.DEV) {
      console.error('操作失败', error)
    }

    const message = error?.response?.data?.message || '操作失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    rejecting.value = false
  }
}

// 格式化金额，添加完整的数据验证
const formatAmount = (amount: number | null | undefined): string => {
  if (amount == null || isNaN(amount)) {
    return '0.00'
  }
  if (amount < 0) {
    return '-' + Math.abs(amount).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
  return amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 状态类型映射
const STATUS_TYPE_MAP: Record<string, string> = {
  draft: 'info',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  paid: 'success',
  verified: 'success'
}

const getStatusType = (status: string): string => {
  return STATUS_TYPE_MAP[status] || 'info'
}

// 状态文本映射
const STATUS_TEXT_MAP: Record<string, string> = {
  draft: '草稿',
  pending: '待审核',
  approved: '已通过',
  rejected: '已拒绝',
  paid: '已付款',
  verified: '已核验'
}

const getStatusText = (status: string): string => {
  return STATUS_TEXT_MAP[status] || status
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
  display: flex;
  gap: 10px;
  justify-content: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>