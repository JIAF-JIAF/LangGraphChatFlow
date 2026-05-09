import React, { useState } from 'react';
import './InputArea.css';

function InputArea({ onSend, loading }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-area">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={loading ? "正在输入..." : "输入消息..."}
        disabled={loading}
        className="input-field"
      />
      <button 
        onClick={handleSend} 
        disabled={loading || !input.trim()}
        className="send-button"
      >
        {loading ? (
          <span className="loading-icon">⏳</span>
        ) : (
          '发送'
        )}
      </button>
    </div>
  );
}

export default InputArea;
