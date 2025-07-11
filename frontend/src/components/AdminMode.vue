<template>
  <div class="admin-mode">
    <h2>管理员控制台</h2>
    
    <div class="admin-buttons">
      <button @click="loadAccounts" :disabled="loading">
        {{ loading ? '加载中...' : '刷新账号列表' }}
      </button>
      <button @click="checkAllAccounts" :disabled="loading">
        检查所有账号
      </button>
    </div>



    <!-- 账号列表表格 -->
    <div v-if="accounts.length" class="accounts-table">
      <h3>👥 账号列表</h3>
      <table>
        <thead>
          <tr>
            <th>用户名</th>
            <th>显示名称</th>
            <th>状态</th>
            <th>乘车记录</th>
            <th>乘车日期</th>
            <th>有效期限</th>
            <th>记录状态</th>
            <th>最后检查</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.username">
            <td>{{ account.username }}</td>
            <td>{{ account.displayName }}</td>
            <td>
              <span :class="['status', account.enabled ? 'enabled' : 'disabled']">
                {{ account.enabled ? '启用' : '禁用' }}
              </span>
            </td>
            <td>
              <span :class="['record-status', getRecordStatusClass(account.hasRecord)]">
                {{ getRecordStatusText(account.hasRecord) }}
              </span>
            </td>
            <td>{{ account.recordDetails?.boardingDate || '-' }}</td>
            <td>{{ account.recordDetails?.expiryDate || '-' }}</td>
            <td>
              <div v-if="account.recordDetails?.status" class="record-detail">
                <div class="status-badge">{{ account.recordDetails.status }}</div>
                <div v-if="account.recordDetails.validityStatus" class="validity-status">
                  {{ account.recordDetails.validityStatus }}
                </div>
              </div>
              <span v-else>-</span>
            </td>
            <td>{{ formatDate(account.lastCheck) }}</td>
            <td class="action-cell">
              <button
                @click="generateRecord(account)"
                :disabled="account.generating || !account.enabled"
                class="generate-btn"
                :class="{ 'generating': account.generating }"
              >
                {{ account.generating ? '生成中...' : '一键生成' }}
              </button>
              <div v-if="account.generating" class="mini-progress">
                {{ account.generateProgress || '准备中...' }}
              </div>
              <div v-if="account.generateResult"
                   class="generate-result"
                   :class="{
                     'result-success': account.generateResult.includes('成功'),
                     'result-error': account.generateResult.includes('失败')
                   }">
                {{ account.generateResult }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="admin-error">
      <h3>❌ 错误信息</h3>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getAccounts, checkAllAccountsRecords } from '../api/admin.js'
import { generateRidingRecord } from '../api/ridingRecord.js'

const loading = ref(false)
const accounts = ref([])
const error = ref('')

const loadAccounts = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await getAccounts()
    // 初始化每个账号的生成状态
    accounts.value = (response.accounts || []).map(account => ({
      ...account,
      generating: false,
      generateProgress: '',
      generateResult: ''
    }))
  } catch (err) {
    error.value = `加载失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

const checkAllAccounts = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await checkAllAccountsRecords()
    // 更新账号列表，包含最新的检查结果，保持生成状态
    const newAccounts = response.accounts || []
    accounts.value = newAccounts.map(newAccount => {
      const existingAccount = accounts.value.find(acc => acc.username === newAccount.username)
      return {
        ...newAccount,
        generating: existingAccount?.generating || false,
        generateProgress: existingAccount?.generateProgress || '',
        generateResult: existingAccount?.generateResult || ''
      }
    })
  } catch (err) {
    error.value = `检查失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 辅助函数
const getRecordStatusClass = (hasRecord) => {
  if (hasRecord === undefined) return 'unknown'
  return hasRecord ? 'has-record' : 'no-record'
}

const getRecordStatusText = (hasRecord) => {
  if (hasRecord === undefined) return '未检查'
  return hasRecord ? '有记录' : '无记录'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生成记录函数
const generateRecord = async (account) => {
  if (!account.enabled) {
    return
  }

  // 设置生成状态
  account.generating = true
  account.generateProgress = ''
  account.generateResult = ''

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
    if (stepIndex < progressSteps.length && account.generating) {
      account.generateProgress = progressSteps[stepIndex]
      stepIndex++
    }
  }, 15000) // 每15秒更新一次进度

  try {
    const response = await generateRidingRecord(account.username, account.password)
    clearInterval(progressInterval)

    if (response.success) {
      account.generateResult = '🎉 生成成功！'
      account.generateProgress = '✅ 生成完成'

      // 生成成功后自动刷新账号列表
      setTimeout(() => {
        loadAccounts()
      }, 2000)
    } else {
      account.generateResult = `❌ 生成失败: ${response.message}`
    }
  } catch (error) {
    clearInterval(progressInterval)
    account.generateResult = `❌ 生成失败: ${error.message}`
  } finally {
    account.generating = false

    // 5秒后清除结果显示
    setTimeout(() => {
      account.generateResult = ''
      account.generateProgress = ''
    }, 5000)
  }
}

// 组件挂载时自动加载账号列表
loadAccounts()
</script>

<style scoped>
.admin-mode {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-buttons {
  display: flex;
  gap: 16px;
  margin-bottom: 30px;
}

.admin-buttons button {
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

.admin-buttons button:hover:not(:disabled) {
  background: #16a085;
}

.admin-buttons button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}



/* 表格样式 */
.accounts-table {
  margin-bottom: 30px;
}

.accounts-table h3 {
  margin-bottom: 16px;
  color: #333;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #18a058;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

td {
  font-size: 14px;
}

tr:hover {
  background: #f8f9fa;
}

/* 状态标签样式 */
.status, .record-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status.enabled {
  background: #d4edda;
  color: #155724;
}

.status.disabled {
  background: #f8d7da;
  color: #721c24;
}

.record-status.has-record {
  background: #d4edda;
  color: #155724;
}

.record-status.no-record {
  background: #fff3cd;
  color: #856404;
}

.record-status.unknown {
  background: #e2e3e5;
  color: #6c757d;
}

.record-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-badge {
  padding: 2px 6px;
  background: #d4edda;
  color: #155724;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  text-align: center;
}

.validity-status {
  font-size: 11px;
  color: #6c757d;
}

/* 错误信息样式 */
.admin-error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.admin-error h3 {
  color: #721c24;
  margin-bottom: 10px;
}

.admin-error p {
  color: #721c24;
  margin: 0;
}

/* 操作列样式 */
.action-cell {
  min-width: 120px;
  text-align: center;
}

.generate-btn {
  background: #18a058;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
}

.generate-btn:hover:not(:disabled) {
  background: #16a085;
  transform: translateY(-1px);
}

.generate-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.generate-btn.generating {
  background: #f39c12;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.mini-progress {
  font-size: 10px;
  color: #666;
  margin-top: 4px;
  padding: 2px 4px;
  background: #f8f9fa;
  border-radius: 3px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.generate-result {
  font-size: 10px;
  margin-top: 4px;
  padding: 2px 4px;
  border-radius: 3px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 成功和失败的样式 */
.result-success {
  background: #d4edda !important;
  color: #155724 !important;
}

.result-error {
  background: #f8d7da !important;
  color: #721c24 !important;
}
</style>
