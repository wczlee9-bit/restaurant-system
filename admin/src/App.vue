<template>
  <div id="app">
    <Login v-if="!isAuthenticated" @login="handleLogin" />
    <AdminLayout v-else @logout="handleLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCurrentUser } from './api/restaurant'
import Login from './views/Login.vue'
import AdminLayout from './components/AdminLayout.vue'

const isAuthenticated = ref(false)
const user = ref(null)

const checkAuth = async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      user.value = await getCurrentUser()
      isAuthenticated.value = true
    } catch {
      localStorage.removeItem('token')
      isAuthenticated.value = false
    }
  }
}

const handleLogin = (token) => {
  localStorage.setItem('token', token)
  isAuthenticated.value = true
  checkAuth()
}

const handleLogout = () => {
  localStorage.removeItem('token')
  isAuthenticated.value = false
  user.value = null
}

onMounted(() => {
  checkAuth()
})
</script>
