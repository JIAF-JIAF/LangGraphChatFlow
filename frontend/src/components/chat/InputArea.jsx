import { useState, memo } from 'react';
import './InputArea.css';

/**
 * 输入区域组件
 * @description 提供消息输入框和发送按钮，支持回车发送
 *
 * @param {Object} props - 组件属性
 * @param {Function} props.onSend - 发送消息回调，接收消息内容字符串
 * @param {boolean} props.loading - 是否正在加载，禁用输入
 * @returns {React.ReactElement}
 */
const InputArea = memo((props) => {
  const { onSend, loading } = props;
  const [input, setInput] = useState('');

  /**
   * 处理发送消息
   */
  const handleSend = () => {
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  /**
   * 处理键盘按键
   * @param {KeyboardEvent} e - 键盘事件
   */
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
        placeholder={loading ? '正在输入...' : '输入消息...'}
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
});

InputArea.displayName = 'InputArea';

export default InputArea;