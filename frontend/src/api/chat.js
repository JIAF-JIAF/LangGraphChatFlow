import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

/**
 * 发送消息到后端
 * @param {string} message - 用户消息
 * @param {string} sessionId - 会话ID
 * @returns {Promise} - 包含回复的 Promise
 */
export const sendMessage = async (message, sessionId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      message: message,
      session_id: sessionId
    });
    return response.data;
  } catch (error) {
    console.error('发送消息失败:', error);
    throw error;
  }
};

/**
 * 检查服务状态
 * @returns {Promise} - 服务状态
 */
export const checkStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/start`);
    return response.data;
  } catch (error) {
    console.error('检查服务状态失败:', error);
    throw error;
  }
};
