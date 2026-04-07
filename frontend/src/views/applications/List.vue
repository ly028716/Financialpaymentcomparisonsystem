<template>
  <div class="application-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>付款申请列表</span>
          <el-button type="primary" @click="$router.push('/applications/create')">
            创建申请
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="申请单号/户名"
            clearable
            maxlength="100"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        class="data-table"
      >
        <el-table-column prop="application_no" label="申请单号" width="180" />
        <el-table-column prop="department" label="部门" width="100" />
        <el-table-column prop="payee_name" label="收款户名" min-width="200" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row.id)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @size-change="fetchData"
        @current-change="fetchData"
      />

      <!-- 空状态 -->
      <el-empty v-if="!tableData.length && !loading" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { applicationApi } from '@/api'
import dayjs from 'dayjs'

// 定义申请数据类型
interface Application {
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

// 定义搜索表单类型
interface SearchForm {
  status: string
  keyword: string
}

// 定义分页类型
interface Pagination {
  page: number
  pageSize: number
  total: number
}

const router = useRouter()
const loading = ref(false)
const tableData = ref<Application[]>([])

const searchForm = reactive<SearchForm>({
  status: '',
  keyword: ''
})

const pagination = reactive<Pagination>({
  page: 1,
  pageSize: 20,
  total: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await applicationApi.getList({
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    })

    if (res?.data) {
      tableData.value = res.data
      pagination.total = res.meta?.total || 0
    }
  } catch (error: any) {
    // 仅在开发环境输出错误信息
    if (import.meta.env.DEV) {
      console.error('获取数据失败', error)
    }

    const message = error?.response?.data?.message || '获取数据失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.status = ''
  searchForm.keyword = ''
  pagination.page = 1
  fetchData()
}

const viewDetail = (id: number) => {
  router.push(`/applications/${id}`)
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

// 格式化日期，添加数据验证
const formatDate = (date: string | null | undefined): string => {
  if (!date) return '-'

  try {
    return dayjs(date).format('YYYY-MM-DD HH:mm')
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('日期格式化失败', error)
    }
    return '-'
  }
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
  fetchData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .search-form {
    display: block;
  }

  .search-form .el-form-item {
    display: block;
    margin-right: 0;
  }
}
</style>