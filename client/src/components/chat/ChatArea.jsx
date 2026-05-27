import { memo } from 'react';
import './ChatArea.css';

/**
 * 聊天消息类型定义
 * @typedef {Object} Message
 * @property {string} type - 消息类型，'user' | 'bot'
 * @property {string} content - 消息内容
 * @property {number} [id] - 消息唯一标识
 * @property {boolean} [isTyping] - 是否正在打字
 */

/**
 * 聊天区域组件
 * @description 展示聊天消息列表，支持打字机效果和加载状态
 *
 * @param {Object} props - 组件属性
 * @param {Message[]} props.messages - 消息列表
 * @param {boolean} props.loading - 是否正在加载
 * @param {string | null} props.currentNode - 当前执行节点
 * @param {Function} props.getNodeLabel - 获取节点显示文本
 * @returns {React.ReactElement}
 */
export const ChatArea = memo((props) => {
  const { messages, loading, currentNode, getNodeLabel } = props;

  return (
    <div className="chat-area">
      {messages.map((msg, index) => (
        <div key={msg.id || index} className={`message-wrapper ${msg.type}`}>
          <div className={`message ${msg.type}`}>
            {msg.type === 'bot' && <div className="message-avatar">🤖</div>}
            <div className="message-content">
              {msg.content}
              {msg.isTyping && <span className="typing-cursor">|</span>}
            </div>
            {msg.type === 'user' && <div className="message-avatar">👤</div>}
          </div>
        </div>
      ))}
      {loading && !messages.some((msg) => msg.isTyping) && (
        <div className="message-wrapper bot">
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              {currentNode ? (
                <div className="node-status">
                  <span className="node-spinner"></span>
                  <span className="node-label">{getNodeLabel(currentNode)}</span>
                </div>
              ) : (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      <div className="messages-end-ref" />
    </div>
  );
});

ChatArea.displayName = 'ChatArea';