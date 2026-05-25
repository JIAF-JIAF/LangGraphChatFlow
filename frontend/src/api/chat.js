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
 * SSE 流式发送消息
 * @param {string} message - 用户消息
 * @param {string} sessionId - 会话ID
 * @param {Object} callbacks - 回调函数
 * @param {Function} callbacks.onToken - 收到 token 时的回调
 * @param {Function} callbacks.onNodeUpdate - 节点更新时的回调
 * @param {Function} callbacks.onDone - 完成时的回调
 * @param {Function} callbacks.onError - 错误时的回调
 * @returns {Promise<void>}
 */
export const sendMessageStream = async (message, sessionId, callbacks) => {
  const { onToken, onNodeUpdate, onDone, onError } = callbacks;

  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            switch (data.type) {
              case 'token':
                onToken?.(data.content, data.node);
                break;
              case 'feeling':
              case 'retrieve':
              case 'plan':
              case 'task':
              case 'node_update':
                onNodeUpdate?.(data);
                break;
              case 'done':
                onDone?.(data);
                break;
              case 'error':
                onError?.(data.error);
                break;
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('SSE 流式请求失败:', error);
    onError?.(error.message);
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
