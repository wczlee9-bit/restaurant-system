<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📋 订单管理</h1>
      <el-button type="primary" @click="loadOrders" :icon="Refresh">刷新</el-button>
    </div>

    <el-table :data="orders" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="order_number" label="订单号" width="180" />
      <el-table-column prop="table_id" label="桌号" width="80" />
      <el-table-column prop="total_amount" label="金额" width="100">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold">¥{{ row.total_amount.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="payment_status" label="支付状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.payment_status === 'paid' ? 'success' : 'warning'">
            {{ row.payment_status === 'paid' ? '已支付' : '未支付' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-dropdown @command="(cmd) => handleStatusChange(row, cmd)">
            <el-button size="small" type="primary">
              更新状态<el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="confirmed">已确认</el-dropdown-item>
                <el-dropdown-item command="preparing">制作中</el-dropdown-item>
                <el-dropdown-item command="ready">已备好</el-dropdown-item>
                <el-dropdown-item command="serving">上菜中</el-dropdown-item>
                <el-dropdown-item command="completed">已完成</el-dropdown-item>
                <el-dropdown-item command="cancelled">已取消</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="600px">
      <div v-if="currentOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="桌号">{{ currentOrder.table_id }} 号桌</el-descriptions-item>
          <el-descriptions-item label="金额">¥{{ currentOrder.total_amount.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentOrder.status)">{{ getStatusLabel(currentOrder.status) }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px; margin-bottom: 10px">订单明细</h3>
        <el-table :data="currentOrder.items" size="small">
          <el-table-column prop="menu_item_id" label="菜品ID" width="100" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="price" label="单价" width="100">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="subtotal" label="小计">
            <template #default="{ row }">¥{{ row.subtotal.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, ArrowDown } from '@element-plus/icons-vue'
import { getOrders, getOrder, updateOrderStatus } from '../api/restaurant'

const loading = ref(false)
const orders = ref([])
const detailVisible = ref(false)
const currentOrder = ref(null)

const loadOrders = async () => {
  loading.value = true
  try {
    orders.value = await getOrders({ store_id: 1 })
    orders.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (error) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (order) => {
  try {
    currentOrder.value = await getOrder(order.id)
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载订单详情失败')
  }
}

const handleStatusChange = async (order, status) => {
  try {
    await ElMessageBox.confirm(`确认将订单 ${order.order_number} 状态更新为 ${getStatusLabel(status)}?`, '确认操作', {
      type: 'warning'
    })

    await updateOrderStatus(order.id, status)
    ElMessage.success('状态更新成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('状态更新失败')
    }
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

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    confirmed: 'success',
    preparing: 'primary',
    ready: 'warning',
    serving: 'danger',
    completed: 'info',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadOrders()
  // 每 30 秒刷新一次
  setInterval(loadOrders, 30000)
})
</script>
