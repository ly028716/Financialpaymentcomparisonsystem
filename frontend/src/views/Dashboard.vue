<template>
  <div class="dashboard" v-loading="loading">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" role="region" aria-label="今日申请统计">
          <div class="stat-title">今日申请</div>
          <div class="stat-value">{{ dashboard.today?.applications || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" role="region" aria-label="今日付款统计">
          <div class="stat-title">今日付款</div>
          <div class="stat-value">{{ dashboard.today?.payments || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card warning" role="region" aria-label="待审核统计">
          <div class="stat-title">待审核</div>
          <div class="stat-value">{{ dashboard.pending?.approvals || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card danger" role="region" aria-label="待复核统计">
          <div class="stat-title">待复核</div>
          <div class="stat-value">{{ dashboard.pending?.reviews || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-row">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/applications/create')">
              创建付款申请
            </el-button>
            <el-button @click="$router.push('/applications')">
              查看申请列表
            </el-button>
            <el-button @click="$router.push('/comparison')">
              对比结果
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>本月统计</span>
          </template>
          <div class="month-stats">
            <p>申请笔数: {{ dashboard.month?.applications || 0 }}</p>
            <p>付款金额: ¥{{ formatAmount(dashboard.month?.amount) }}</p>
            <p>差异笔数: {{ dashboard.month?.differences || 0 }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!hasData && !loading" description="暂无数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { reportApi } from '@/api'
import { ElMessage } from 'element-plus'

// 定义仪表盘数据类型
interface DashboardData {
  today?: {
    applications: number
    payments: number
  }
  pending?: {
    approvals: number
    reviews: number
  }
  month?: {
    applications: number
    amount: number
    differences: number
  }
}

const dashboard = ref<DashboardData>({})
const loading = ref(false)

// 检查是否有数据
const hasData = computed(() => {
  return dashboard.value.today || dashboard.value.pending || dashboard.value.month
})

// 格式化金额，添加数据验证
const formatAmount = (amount: number | null | undefined): string => {
  if (amount == null || isNaN(amount)) {
    return '0.00'
  }
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await reportApi.getDashboard()
    if (res?.data) {
      dashboard.value = res.data
    }
  } catch (error) {
    // 仅在开发环境输出错误信息
    if (import.meta.env.DEV) {
      console.error('获取仪表盘数据失败', error)
    }
    ElMessage.error('加载仪表盘数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-title {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-top: 10px;
}

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.stat-card.danger .stat-value {
  color: #f56c6c;
}

.dashboard-row {
  margin-top: 20px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.month-stats p {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .quick-actions {
    flex-direction: column;
  }

  .quick-actions .el-button {
    width: 100%;
  }
}
</style>