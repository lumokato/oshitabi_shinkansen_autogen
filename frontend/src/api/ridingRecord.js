import api from './index.js'
import axios from 'axios'

// 为生成功能创建专门的API实例（更长的超时时间）
const generateApi = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟超时，适应完整的自动化流程
  headers: {
    'Content-Type': 'application/json'
  }
})

// 生成API的响应拦截器
generateApi.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.message || error.message || '生成失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * 检查乘车记录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise} 查询结果
 */
export const checkRidingRecord = async (username, password) => {
  const response = await api.post('/riding-record/check', {
    username,
    password
  })
  return response
}

/**
 * 生成乘车记录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise} 生成结果
 */
export const generateRidingRecord = async (username, password) => {
  const response = await generateApi.post('/riding-record/generate', {
    username,
    password
  })
  return response
}
