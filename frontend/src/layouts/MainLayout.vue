<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h1>财务付款对比系统</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <el-menu-item index="/applications">
          <el-icon><Document /></el-icon>
          <span>付款申请</span>
        </el-menu-item>

        <el-menu-item index="/payments">
          <el-icon><Coin /></el-icon>
          <span>付款记录</span>
        </el-menu-item>

        <el-menu-item index="/comparison">
          <el-icon><Switch /></el-icon>
          <span>对比结果</span>
        </el-menu-item>

        <el-menu-item index="/reports">
          <el-icon><TrendCharts /></el-icon>
          <span>报表统计</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="User" />
              <span class="username">{{ userName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { DataAnalysis, Document, Coin, Switch, TrendCharts } from '@element-plus/icons-vue'
import { authApi } from '@/api'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

const userName = computed(() => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user).name : '用户'
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'logout':
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await authApi.logout()
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      break
    case 'password':
      // TODO: 打开修改密码对话框
      break
    case 'profile':
      // TODO: 打开个人信息页面
      break
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo h1 {
  color: #fff;
  font-size: 16px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 10px;
}

.header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: #303133;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>