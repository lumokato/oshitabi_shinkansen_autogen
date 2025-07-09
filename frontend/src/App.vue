<template>
  <div class="app-container">
    <h1>🚄 乘车记录管理系统</h1>

    <div class="mode-switch">
      <button @click="isAdminMode = false" :class="{ active: !isAdminMode }">
        普通模式
      </button>
      <button @click="isAdminMode = true" :class="{ active: isAdminMode }">
        管理员模式
      </button>
    </div>

    <div class="content">
      <UserMode v-if="!isAdminMode" />

      <div v-else class="admin-mode">
        <AdminLogin v-if="!isAdminAuthenticated" @login-success="handleAdminLogin" />
        <AdminMode v-else />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UserMode from './components/UserMode.vue'
import AdminLogin from './components/AdminLogin.vue'
import AdminMode from './components/AdminMode.vue'

const isAdminMode = ref(false)
const isAdminAuthenticated = ref(false)

// 处理管理员登录成功
const handleAdminLogin = () => {
  isAdminAuthenticated.value = true
}


</script>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #18a058;
  margin-bottom: 30px;
}

.mode-switch {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}

.mode-switch button {
  padding: 10px 20px;
  border: 2px solid #18a058;
  background: white;
  color: #18a058;
  cursor: pointer;
  border-radius: 5px;
  transition: all 0.3s;
}

.mode-switch button.active {
  background: #18a058;
  color: white;
}

.mode-switch button:hover {
  background: #18a058;
  color: white;
}

.content {
  min-height: 400px;
}


</style>
