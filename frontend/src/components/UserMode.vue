<template>
  <div class="user-mode">
    <h2>普通用户模式</h2>
    <div class="form">
      <input v-model="username" placeholder="请输入用户名" />
      <input v-model="password" type="password" placeholder="请输入密码" />
      <div class="buttons">
        <button @click="checkRecord" :disabled="loading">
          {{ loading ? '查询中...' : '查询乘车记录' }}
        </button>
        <button @click="generateRecord" :disabled="generating">
          {{ generateButtonText }}
        </button>
      </div>
    </div>

    <!-- 生成进度显示 -->
    <div v-if="generating" class="progress-card">
      <h3>🤖 自动化进行中</h3>
      <div class="progress-content">
        <div class="progress-text">{{ generateProgress || '准备中...' }}</div>
        <div class="progress-time">已用时: {{ Math.floor((Date.now() - (generateStartTime || Date.now())) / 1000) }}秒</div>
        <div class="progress-tip">
          💡 提示：自动化流程需要1-3分钟，请耐心等待...
        </div>
      </div>
    </div>

    <div v-if="result" class="result">
      <h3>📋 查询结果</h3>
      <p>{{ result }}</p>

      <!-- 详细信息显示 -->
      <div v-if="queryDetails" class="details">
        <h4>详细信息：</h4>
        <div class="detail-item">
          <span>🚄 乘车日期：</span>
          <span>{{ queryDetails.riding_date || '未知' }}</span>
        </div>
        <div class="detail-item">
          <span>📅 有效期限：</span>
          <span>{{ queryDetails.expiry_date || '未知' }}</span>
        </div>
        <div class="detail-item">
          <span>✅ 状态：</span>
          <span>{{ queryDetails.status || '未知' }}</span>
        </div>
        <div class="detail-item">
          <span>⏰ 有效期状态：</span>
          <span>{{ queryDetails.expiry_status || '未知' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { checkRidingRecord, generateRidingRecord } from '../api/ridingRecord.js'

const username = ref('')
const password = ref('')
const loading = ref(false)
const generating = ref(false)
const result = ref('')
const queryDetails = ref(null)
const generateProgress = ref('')
const generateStartTime = ref(null)

// 计算生成按钮文本
const generateButtonText = computed(() => {
  if (!generating.value) return '一键生成记录'

  if (generateProgress.value) {
    return generateProgress.value
  }

  const elapsed = generateStartTime.value ?
    Math.floor((Date.now() - generateStartTime.value) / 1000) : 0
  return `生成中... (${elapsed}s)`
})

const checkRecord = async () => {
  if (!username.value || !password.value) {
    result.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  result.value = ''
  queryDetails.value = null

  try {
    const response = await checkRidingRecord(username.value, password.value)

    // 构建结果消息
    let message = response.hasRecord ? '✅ 已有乘车记录' : '❌ 暂无乘车记录'

    // 如果是新保存的用户，添加提示
    if (response.userSaved) {
      message += '\n💾 用户信息已保存到配置文件'
    }

    result.value = message

    // 保存详细信息
    if (response.hasRecord && response.details) {
      queryDetails.value = response.details
    }
  } catch (error) {
    result.value = `查询失败: ${error.message}`
  } finally {
    loading.value = false
  }
}

const generateRecord = async () => {
  if (!username.value || !password.value) {
    result.value = '请输入用户名和密码'
    return
  }

  generating.value = true
  result.value = ''
  generateStartTime.value = Date.now()

  // 模拟进度更新
  const progressSteps = [
    '🌐 启动无头浏览器...',
    '🔑 执行登录...',
    '🚀 执行自动化脚本...',
    '📝 填写问卷...',
    '✅ 完成生成...'
  ]

  let stepIndex = 0
  const progressInterval = setInterval(() => {
    if (stepIndex < progressSteps.length && generating.value) {
      generateProgress.value = progressSteps[stepIndex]
      stepIndex++
    }
  }, 15000) // 每15秒更新一次进度

  try {
    const response = await generateRidingRecord(username.value, password.value)
    clearInterval(progressInterval)

    if (response.success) {
      result.value = '🎉 乘车记录生成成功！'
      generateProgress.value = '✅ 生成完成'

      // 生成成功后自动查询最新记录
      setTimeout(() => {
        checkRecord()
      }, 1000)
    } else {
      result.value = `❌ 生成失败: ${response.message}`
    }
  } catch (error) {
    clearInterval(progressInterval)
    result.value = `❌ 生成失败: ${error.message}`
  } finally {
    generating.value = false
    generateProgress.value = ''
    generateStartTime.value = null
  }
}
</script>

<style scoped>
.user-mode {
  max-width: 600px;
  margin: 0 auto;
}

.form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.form input {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form input:focus {
  outline: none;
  border-color: #18a058;
}

.buttons {
  display: flex;
  gap: 12px;
}

.buttons button {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.buttons button:first-child {
  background: #18a058;
  color: white;
}

.buttons button:first-child:hover:not(:disabled) {
  background: #16a085;
}

.buttons button:last-child {
  background: #2080f0;
  color: white;
}

.buttons button:last-child:hover:not(:disabled) {
  background: #1c7ed6;
}

.buttons button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.result h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.result p {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
}

/* 详细信息样式 */
.details {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.details h4 {
  margin: 0 0 12px 0;
  color: #495057;
  font-size: 16px;
}

.detail-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item span:first-child {
  font-weight: 600;
  color: #495057;
  min-width: 120px;
  margin-right: 12px;
}

.detail-item span:last-child {
  color: #212529;
  font-weight: 500;
}

/* 进度显示样式 */
.progress-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.progress-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-text {
  font-size: 16px;
  font-weight: 500;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  backdrop-filter: blur(10px);
}

.progress-time {
  font-size: 14px;
  opacity: 0.9;
}

.progress-tip {
  font-size: 13px;
  opacity: 0.8;
  font-style: italic;
  margin-top: 8px;
}
</style>