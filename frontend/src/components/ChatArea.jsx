import React, { useEffect, useRef } from 'react';
import './ChatArea.css';

function ChatArea({ messages, loading }) {
  const messagesEndRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

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
      {loading && !messages.some(msg => msg.isTyping) && (
        <div className="message-wrapper bot">
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatArea;
