<template>
  <div id="app">
    <Menu v-if="currentView === 'menu'" @order-created="handleOrderCreated" />
    <OrderSuccess v-else-if="currentView === 'success'" :order="currentOrder" @back="currentView = 'menu'" />
    <OrderDetail v-else-if="currentView === 'detail'" :order-id="currentOrderId" @back="currentView = 'success'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Menu from './views/Menu.vue'
import OrderSuccess from './views/OrderSuccess.vue'
import OrderDetail from './views/OrderDetail.vue'

const currentView = ref('menu')
const currentOrder = ref(null)
const currentOrderId = ref(null)

const handleOrderCreated = (order) => {
  currentOrder.value = order
  currentOrderId.value = order.id
  currentView.value = 'success'
}
</script>
