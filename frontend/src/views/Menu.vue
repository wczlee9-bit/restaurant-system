<template>
  <div class="menu-container">
    <header class="header">
      <h1>🍽️ 扫码点餐</h1>
      <p class="table-info">桌号：{{ tableId }}</p>
    </header>

    <div class="main-content">
      <div class="menu-list">
        <h2 class="section-title">菜单</h2>
        <div class="menu-items" v-if="menuItems.length > 0">
          <div
            v-for="item in menuItems"
            :key="item.id"
            class="menu-item"
            :class="{ disabled: !item.is_available || item.stock <= 0 }"
          >
            <div class="item-info">
              <h3 class="item-name">{{ item.name }}</h3>
              <p class="item-desc">{{ item.description }}</p>
              <p class="item-price">¥{{ item.price.toFixed(2) }}</p>
              <p v-if="item.stock <= 10" class="stock-warning">库存紧张：{{ item.stock }} 份</p>
            </div>
            <div class="item-actions">
              <button
                @click="addToCart(item)"
                :disabled="!item.is_available || item.stock <= 0"
                class="btn-add"
              >
                {{ item.is_available && item.stock > 0 ? '加入购物车' : '已售罄' }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="loading">
          加载中...
        </div>
      </div>

      <div class="cart-panel">
        <h2 class="section-title">购物车</h2>
        <div v-if="cart.length > 0" class="cart-items">
          <div v-for="(item, index) in cart" :key="index" class="cart-item">
            <div class="cart-item-info">
              <span class="cart-item-name">{{ item.name }}</span>
              <span class="cart-item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
            <div class="cart-item-controls">
              <button @click="decreaseQuantity(index)" class="btn-control">-</button>
              <span class="quantity">{{ item.quantity }}</span>
              <button @click="increaseQuantity(index)" class="btn-control">+</button>
            </div>
          </div>
        </div>
        <div v-else class="cart-empty">
          购物车为空
        </div>
        <div v-if="cart.length > 0" class="cart-summary">
          <div class="total">
            <span>总计：</span>
            <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
          </div>
          <textarea
            v-model="specialRequirements"
            class="requirements-input"
            placeholder="特殊要求（选填）"
            rows="3"
          ></textarea>
          <button @click="submitOrder" class="btn-submit" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交订单' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getMenu, createOrder } from '../api/restaurant'

const emit = defineEmits(['orderCreated'])

const tableId = ref(1)
const storeId = ref(1)
const menuItems = ref([])
const cart = ref([])
const specialRequirements = ref('')
const submitting = ref(false)

const totalPrice = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const loadMenu = async () => {
  try {
    menuItems.value = await getMenu(storeId.value)
  } catch (error) {
    alert('加载菜单失败：' + error.message)
  }
}

const addToCart = (item) => {
  const existingItem = cart.value.find(c => c.id === item.id)
  if (existingItem) {
    if (existingItem.quantity < item.stock) {
      existingItem.quantity++
    } else {
      alert('库存不足')
    }
  } else {
    cart.value.push({
      id: item.id,
      name: item.name,
      price: item.price,
      quantity: 1,
      maxStock: item.stock
    })
  }
}

const increaseQuantity = (index) => {
  const item = cart.value[index]
  if (item.quantity < item.maxStock) {
    item.quantity++
  } else {
    alert('库存不足')
  }
}

const decreaseQuantity = (index) => {
  const item = cart.value[index]
  if (item.quantity > 1) {
    item.quantity--
  } else {
    cart.value.splice(index, 1)
  }
}

const submitOrder = async () => {
  if (cart.value.length === 0) {
    alert('请先添加菜品到购物车')
    return
  }

  submitting.value = true
  try {
    const orderData = {
      table_id: tableId.value,
      store_id: storeId.value,
      items: cart.value.map(item => ({
        menu_item_id: item.id,
        quantity: item.quantity
      })),
      special_requirements: specialRequirements.value || null
    }

    const order = await createOrder(orderData)
    emit('orderCreated', order)
    cart.value = []
    specialRequirements.value = ''
  } catch (error) {
    alert('提交订单失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // 从 URL 获取桌号
  const urlParams = new URLSearchParams(window.location.search)
  if (urlParams.get('table')) {
    tableId.value = parseInt(urlParams.get('table'))
  }
  if (urlParams.get('store')) {
    storeId.value = parseInt(urlParams.get('store'))
  }

  loadMenu()
})
</script>

<style scoped>
.menu-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 10px;
}

.table-info {
  font-size: 1.1rem;
  color: #666;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 15px;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.menu-item.disabled {
  opacity: 0.5;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 5px;
}

.item-desc {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.item-price {
  font-size: 1.2rem;
  color: #ff6b6b;
  font-weight: bold;
}

.stock-warning {
  font-size: 0.8rem;
  color: #ffa500;
}

.btn-add {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-add:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.cart-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.cart-item-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.cart-item-name {
  font-size: 0.95rem;
  color: #333;
}

.cart-item-price {
  font-size: 0.9rem;
  color: #ff6b6b;
}

.cart-item-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity {
  font-size: 1rem;
  color: #333;
  min-width: 30px;
  text-align: center;
}

.btn-control {
  width: 30px;
  height: 30px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.cart-empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.loading {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.cart-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #eee;
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 15px;
}

.total-price {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.4rem;
}

.requirements-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 0.9rem;
  resize: none;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
