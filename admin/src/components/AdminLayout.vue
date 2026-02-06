<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="header-left">
        <h2>🍽️ 餐厅管理系统</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="admin-main">
      <el-tabs v-model="activeTab" type="card" @tab-change="handleTabChange">
        <el-tab-pane label="数据统计" name="stats">
          <StatsView />
        </el-tab-pane>
        <el-tab-pane label="订单管理" name="orders">
          <OrdersView />
        </el-tab-pane>
        <el-tab-pane label="菜单管理" name="menu">
          <MenuView />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCurrentUser } from '../api/restaurant'
import StatsView from '../views/StatsView.vue'
import OrdersView from '../views/OrdersView.vue'
import MenuView from '../views/MenuView.vue'

const emit = defineEmits(['logout'])

const activeTab = ref('stats')
const user = ref(null)

const loadUser = async () => {
  try {
    user.value = await getCurrentUser()
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

const handleTabChange = (tab) => {
  activeTab.value = tab
}

const handleCommand = (command) => {
  if (command === 'logout') {
    emit('logout')
  }
}

onMounted(() => {
  loadUser()
})
</script>

<style scoped>
.header-left h2 {
  font-size: 1.3rem;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  font-size: 1rem;
}

:deep(.el-tabs) {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

:deep(.el-tabs__content) {
  padding-top: 20px;
}
</style>
