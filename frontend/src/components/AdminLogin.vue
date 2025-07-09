<template>
  <div class="admin-login">
    <h2>管理员登录</h2>
    <div class="login-form">
      <input 
        v-model="password" 
        type="password" 
        placeholder="请输入管理员密码"
        @keyup.enter="handleLogin"
      />
      <button @click="handleLogin" :disabled="!password">登录</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { adminLogin } from '../api/admin.js'

const emit = defineEmits(['login-success'])

const password = ref('')
const error = ref('')

const handleLogin = async () => {
  if (!password.value) {
    error.value = '请输入管理员密码'
    return
  }

  try {
    const response = await adminLogin(password.value)

    if (response.success) {
      emit('login-success')
      error.value = ''
    } else {
      error.value = response.message || '密码错误'
    }
  } catch (err) {
    error.value = err.message || '登录失败'
  }
}
</script>

<style scoped>
.admin-login {
  max-width: 400px;
  margin: 0 auto;
}

.login-form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  text-align: center;
}

.login-form input {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.login-form input:focus {
  outline: none;
  border-color: #18a058;
}

.login-form button {
  width: 100%;
  padding: 12px 24px;
  background: #18a058;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.login-form button:hover:not(:disabled) {
  background: #16a085;
}

.login-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  margin: 16px 0 0 0;
  font-size: 14px;
}
</style>
