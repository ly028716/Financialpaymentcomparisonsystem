import axios from 'axios'
import type { AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

// 注意：当前使用 localStorage 存储 token 存在 XSS 风险
// 建议：生产环境应使用 httpOnly cookie 配合 CSRF token
// 或实施严格的 CSP (Content Security Policy) 策略
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response
    // 检查响应格式，确保有 code 字段
    if (typeof data === 'object' && data !== null && 'code' in data) {
      if (data.code !== 200 && data.code !== 201) {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(new Error(data.message || '请求失败'))
      }
    }
    return data
  },
  (error: AxiosError<any>) => {
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          // 使用路由导航而不是直接修改 location，避免 Open Redirect 风险
          // 注意：这里需要在实际使用时导入 router
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default api

// API 类型定义
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  meta?: {
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

// 认证接口
export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post<ApiResponse>('/auth/login/', data),

  logout: () => api.post<ApiResponse>('/auth/logout/'),

  getMe: () => api.get<ApiResponse>('/auth/me/'),

  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post<ApiResponse>('/auth/change-password/', data)
}

// 付款申请接口
export const applicationApi = {
  getList: (params?: any) => api.get<ApiResponse>('/applications/', { params }),

  getMy: (params?: any) => api.get<ApiResponse>('/applications/my/', { params }),

  getPending: (params?: any) => api.get<ApiResponse>('/applications/pending/', { params }),

  getDetail: (id: number) => api.get<ApiResponse>(`/applications/${id}/`),

  create: (data: any) => api.post<ApiResponse>('/applications/', data),

  update: (id: number, data: any) => api.put<ApiResponse>(`/applications/${id}/`, data),

  delete: (id: number) => api.delete<ApiResponse>(`/applications/${id}/`),

  approve: (id: number, note?: string) =>
    api.put<ApiResponse>(`/applications/${id}/approve/`, { note }),

  reject: (id: number, reason: string, note?: string) =>
    api.put<ApiResponse>(`/applications/${id}/reject/`, { reason, note }),

  batchApprove: (applicationIds: number[], action: 'approve' | 'reject', note?: string) =>
    api.post<ApiResponse>('/applications/batch-approve/', {
      application_ids: applicationIds,
      action,
      note
    }),

  export: (params?: any) =>
    api.get('/applications/export/', { params, responseType: 'blob' })
}

// 付款记录接口
export const paymentApi = {
  getList: (params?: any) => api.get<ApiResponse>('/payments/', { params }),

  getPending: (params?: any) => api.get<ApiResponse>('/payments/pending/', { params }),

  getDetail: (id: number) => api.get<ApiResponse>(`/payments/${id}/`),

  create: (data: any) => api.post<ApiResponse>('/payments/', data),

  batch: (payments: any[]) =>
    api.post<ApiResponse>('/payments/batch/', { payments }),

  ocr: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ApiResponse>('/payments/ocr/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 对比结果接口
export const comparisonApi = {
  getList: (params?: any) => api.get<ApiResponse>('/comparison/', { params }),

  getDifferences: (params?: any) => api.get<ApiResponse>('/comparison/differences/', { params }),

  getDetail: (id: number) => api.get<ApiResponse>(`/comparison/${id}/`),

  verify: (id: number, result: 'normal' | 'abnormal', note?: string) =>
    api.put<ApiResponse>(`/comparison/${id}/verify/`, { result, note }),

  trigger: (applicationId: number, paymentId: number) =>
    api.post<ApiResponse>('/comparison/trigger/', {
      application_id: applicationId,
      payment_id: paymentId
    })
}

// 报表接口
export const reportApi = {
  getDashboard: () => api.get<ApiResponse>('/reports/dashboard/'),

  getPaymentStats: (params?: any) =>
    api.get<ApiResponse>('/reports/payment-stats/', { params }),

  getDifferenceAnalysis: (params?: any) =>
    api.get<ApiResponse>('/reports/difference-analysis/', { params }),

  getEfficiencyAnalysis: (params?: any) =>
    api.get<ApiResponse>('/reports/efficiency-analysis/', { params })
}

// 文件接口
export const fileApi = {
  upload: (file: File, type?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (type) formData.append('type', type)
    return api.post<ApiResponse>('/files/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  download: (fileId: string) =>
    api.get(`/files/${fileId}/download/`, { responseType: 'blob' })
}