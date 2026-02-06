<template>
  <div class="success-container">
    <div class="success-card">
      <div class="success-icon">✅</div>
      <h1>订单提交成功</h1>
      <p class="order-number">订单号：{{ order.order_number }}</p>

      <div class="order-info">
        <div class="info-item">
          <span class="label">桌号：</span>
          <span class="value">{{ order.table_id }} 号桌</span>
        </div>
        <div class="info-item">
          <span class="label">总金额：</span>
          <span class="value price">¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
        <div class="info-item">
          <span class="label">状态：</span>
          <span class="value status" :class="order.status">
            {{ getStatusText(order.status) }}
          </span>
        </div>
      </div>

      <div class="actions">
        <button @click="viewDetail" class="btn-primary">查看订单详情</button>
        <button @click="back" class="btn-secondary">返回菜单</button>
      </div>

      <p class="tip">💡 您的订单已提交，请耐心等待</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  order: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back'])

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

const viewDetail = () => {
  emit('view-detail', props.order.id)
}

const back = () => {
  emit('back')
}
</script>

<style scoped>
.success-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.success-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
  text-align: center;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.success-card h1 {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 10px;
}

.order-number {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 30px;
}

.order-info {
  text-align: left;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.label {
  color: #666;
}

.value {
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
}

.value.status.pending { background: #fff3cd; color: #856404; }
.value.status.confirmed { background: #d4edda; color: #155724; }
.value.status.preparing { background: #cce5ff; color: #004085; }
.value.status.ready { background: #d1ecf1; color: #0c5460; }
.value.status.completed { background: #d4edda; color: #155724; }
.value.status.cancelled { background: #f8d7da; color: #721c24; }

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.tip {
  color: #999;
  font-size: 0.9rem;
}
</style>
