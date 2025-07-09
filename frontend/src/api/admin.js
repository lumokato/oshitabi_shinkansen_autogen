import api from './index.js'

/**
 * 管理员登录
 * @param {string} password 管理员密码
 * @returns {Promise} 登录结果
 */
export const adminLogin = async (password) => {
  const response = await api.post('/admin/login', {
    password
  })
  return response
}

/**
 * 获取所有账号信息
 * @returns {Promise} 账号列表和统计信息
 */
export const getAccounts = async () => {
  const response = await api.get('/admin/accounts')
  return response
}

/**
 * 批量生成乘车记录
 * @param {Array} usernames 用户名列表
 * @returns {Promise} 批量操作结果
 */
export const batchGenerateRecords = async (usernames) => {
  const response = await api.post('/admin/batch-generate', {
    usernames
  })
  return response
}

/**
 * 检查所有账号的乘车记录
 * @returns {Promise} 检查结果
 */
export const checkAllAccountsRecords = async () => {
  const response = await api.post('/admin/check-all')
  return response
}
