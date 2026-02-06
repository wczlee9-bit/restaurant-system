<template>
  <div class="detail-container">
    <div class="detail-card">
      <header class="detail-header">
        <button @click="back" class="btn-back">← 返回</button>
        <h1>订单详情</h1>
      </header>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="order" class="order-detail">
        <div class="detail-section">
          <h2>订单信息</h2>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">订单号：</span>
              <span class="value">{{ order.order_number }}</span>
            </div>
            <div class="info-item">
              <span class="label">桌号：</span>
              <span class="value">{{ order.table_id }} 号桌</span>
            </div>
            <div class="info-item">
              <span class="label">下单时间：</span>
              <span class="value">{{ formatTime(order.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态：</span>
              <span class="value status" :class="order.status">
                {{ getStatusText(order.status) }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">支付状态：</span>
              <span class="value payment" :class="order.payment_status">
                {{ getPaymentStatusText(order.payment_status) }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">总金额：</span>
              <span class="value price">¥{{ order.total_amount.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h2>订单明细</h2>
          <div class="order-items">
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <div class="item-info">
                <span class="item-name">菜品 #{{ item.menu_item_id }}</span>
                <span class="item-quantity">x{{ item.quantity }}</span>
              </div>
              <div class="item-price">¥{{ item.subtotal.toFixed(2) }}</div>
            </div>
          </div>
        </div>

        <div v-if="order.special_requirements" class="detail-section">
          <h2>特殊要求</h2>
          <p class="requirements">{{ order.special_requirements }}</p>
        </div>
      </div>

      <div v-else class="error">
        加载订单详情失败
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrder } from '../api/restaurant'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['back'])

const loading = ref(true)
const order = ref(null)

const loadOrder = async () => {
  loading.value = true
  try {
    order.value = await getOrder(props.orderId)
  } catch (error) {
    console.error('加载订单详情失败：', error)
  } finally {
    loading.value = false
  }
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待确认',
    confirmed: '已确认',
    preparing: '制作中',
    ready: '已备好',
    serving: '上菜中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getPaymentStatusText = (status) => {
  const statusMap = {
    unpaid: '未支付',
    paid: '已支付',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

const formatTime = (time) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const back = () => {
  emit('back')
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  padding: 20px;
}

.detail-card {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.detail-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-back {
  padding: 8px 16px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #333;
}

.detail-header h1 {
  font-size: 1.3rem;
  color: #333;
}

.detail-section {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.detail-section h2 {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

@media (max-width: 600px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label {
  font-size: 0.9rem;
  color: #666;
}

.value {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.value.price {
  color: #ff6b6b;
  font-size: 1.2rem;
}

.value.status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  display: inline-block;
}

.value.status.pending { background: #fff3cd; color: #856404; }
.value.status.confirmed { background: #d4edda; color: #155724; }
.value.status.preparing { background: #cce5ff; color: #004085; }
.value.status.ready { background: #d1ecf1; color: #0c5460; }
.value.status.completed { background: #d4edda; color: #155724; }
.value.status.cancelled { background: #f8d7da; color: #721c24; }

.value.payment {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  display: inline-block;
}

.value.payment.unpaid { background: #f8d7da; color: #721c24; }
.value.payment.paid { background: #d4edda; color: #155724; }
.value.payment.refunded { background: #f0f0f0; color: #666; }

.order-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-name {
  color: #333;
}

.item-quantity {
  color: #666;
}

.item-price {
  color: #ff6b6b;
  font-weight: 500;
}

.requirements {
  color: #666;
  line-height: 1.6;
}

.loading,
.error {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.error {
  color: #ff6b6b;
}
</style>
