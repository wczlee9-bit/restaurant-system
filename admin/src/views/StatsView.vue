<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📊 数据统计</h1>
    </div>

    <div class="page-stats" v-loading="loading">
      <div class="stat-card">
        <div class="stat-label">今日订单</div>
        <div class="stat-value">{{ stats.todayOrders || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">今日营收</div>
        <div class="stat-value">¥{{ (stats.todayRevenue || 0).toFixed(2) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">待处理订单</div>
        <div class="stat-value">{{ stats.pendingOrders || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">菜品数量</div>
        <div class="stat-value">{{ stats.totalMenuItems || 0 }}</div>
      </div>
    </div>

    <div class="charts-container">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>订单状态分布</span>
          </div>
        </template>
        <div class="status-chart">
          <div v-for="(count, status) in orderStatusStats" :key="status" class="status-item">
            <span class="status-label">{{ getStatusLabel(status) }}:</span>
            <el-progress :percentage="getPercentage(count)" :color="getStatusColor(status)" />
            <span class="status-count">{{ count }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrders, getMenu } from '../api/restaurant'

const loading = ref(false)
const stats = ref({})
const orderStatusStats = ref({})

const loadStats = async () => {
  loading.value = true
  try {
    // 获取所有订单
    const orders = await getOrders({ store_id: 1 })

    // 计算今日订单和营收
    const today = new Date().toDateString()
    const todayOrders = orders.filter(o => new Date(o.created_at).toDateString() === today)
    const todayRevenue = todayOrders.reduce((sum, o) => sum + o.total_amount, 0)

    // 计算待处理订单
    const pendingOrders = orders.filter(o => o.status === 'pending' || o.status === 'confirmed').length

    // 订单状态统计
    const statusMap = {}
    orders.forEach(order => {
      statusMap[order.status] = (statusMap[order.status] || 0) + 1
    })

    // 获取菜单数量
    const menuItems = await getMenu(1)

    stats.value = {
      todayOrders: todayOrders.length,
      todayRevenue,
      pendingOrders,
      totalMenuItems: menuItems.length,
      totalOrders: orders.length
    }

    orderStatusStats.value = statusMap
  } catch (error) {
    console.error('加载统计数据失败', error)
  } finally {
    loading.value = false
  }
}

const getStatusLabel = (status) => {
  const map = {
    pending: '待确认',
    confirmed: '已确认',
    preparing: '制作中',
    ready: '已备好',
    serving: '上菜中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getStatusColor = (status) => {
  const map = {
    pending: '#909399',
    confirmed: '#67C23A',
    preparing: '#409EFF',
    ready: '#E6A23C',
    serving: '#F56C6C',
    completed: '#909399',
    cancelled: '#F56C6C'
  }
  return map[status] || '#909399'
}

const getPercentage = (count) => {
  const total = Object.values(orderStatusStats.value).reduce((a, b) => a + b, 0)
  return total > 0 ? Math.round((count / total) * 100) : 0
}

onMounted(() => {
  loadStats()
  // 每 30 秒刷新一次
  setInterval(loadStats, 30000)
})
</script>

<style scoped>
.charts-container {
  margin-top: 20px;
}

.card-header {
  font-size: 1.1rem;
  font-weight: bold;
}

.status-chart {
  padding: 20px 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.status-label {
  width: 100px;
  font-size: 0.95rem;
}

.status-count {
  width: 50px;
  text-align: right;
  font-weight: bold;
}
</style>
