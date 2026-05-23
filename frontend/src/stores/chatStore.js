import { create } from 'zustand';
import { sendMessage as sendMessageApi } from '../api/chat';

/**
 * 聊天消息类型定义
 * @typedef {Object} Message
 * @property {string} type - 消息类型，'user' | 'bot'
 * @property {string} content - 消息内容
 * @property {number} [id] - 消息唯一标识
 * @property {boolean} [isTyping] - 是否正在打字
 */

/**
 * 聊天状态管理 Store
 * @description 管理聊天消息、会话状态、发送消息等
 *
 * @returns {Object} 聊天状态和方法
 *
 * @example
 * ```jsx
 * const { messages, loading, sendMessage } = useChatStore();
 * await sendMessage('你好');
 * ```
 */
const useChatStore = create((set, get) => ({
  /**
   * 消息列表
   * @type {Message[]}
   */
  messages: [
    { type: 'bot', content: '您好！我是智能客服，有什么可以帮助您的吗？' }
  ],

  /**
   * 会话 ID
   * @type {string}
   */
  sessionId: Date.now().toString(),

  /**
   * 加载状态
   * @type {boolean}
   */
  loading: false,

  /**
   * 添加用户消息
   * @param {string} content - 消息内容
   */
  addUserMessage: (content) => {
    set((state) => ({
      messages: [...state.messages, { type: 'user', content }]
    }));
  },

  /**
   * 添加机器人消息
   * @param {string} content - 消息内容
   * @param {number} [id] - 消息 ID，默认为当前时间戳
   */
  addBotMessage: (content, id = Date.now()) => {
    set((state) => ({
      messages: [...state.messages, { type: 'bot', content, id, isTyping: true }]
    }));
  },

  /**
   * 更新消息内容
   * @param {number} id - 消息 ID
   * @param {string} content - 新内容
   * @param {boolean} [isTyping] - 是否正在打字
   */
  updateMessage: (id, content, isTyping = false) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content, isTyping } : msg
      )
    }));
  },

  /**
   * 打字机效果显示文本
   * @param {string} fullText - 完整文本内容
   */
  typeWriter: async (fullText) => {
    const messageId = Date.now();
    const { addBotMessage, updateMessage } = get();

    addBotMessage('', messageId);

    for (let i = 0; i < fullText.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 30));
      updateMessage(messageId, fullText.substring(0, i + 1));
    }

    updateMessage(messageId, fullText, false);
  },

  /**
   * 发送消息
   * @param {string} message - 用户输入的消息
   */
  sendMessage: async (message) => {
    const { addUserMessage, typeWriter, setLoading } = get();

    addUserMessage(message);
    setLoading(true);

    try {
      const response = await sendMessageApi(message, get().sessionId);
      if (response.reply) {
        await typeWriter(response.reply);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      await typeWriter('抱歉，服务暂时不可用，请稍后再试。');
    } finally {
      setLoading(false);
    }
  },

  /**
   * 设置加载状态
   * @param {boolean} loading - 加载状态
   */
  setLoading: (loading) => set({ loading }),

  /**
   * 重置会话
   * @description 清空消息列表并生成新的会话 ID
   */
  resetSession: () => set({
    messages: [{ type: 'bot', content: '您好！我是智能客服，有什么可以帮助您的吗？' }],
    sessionId: Date.now().toString()
  })
}));

export default useChatStore;