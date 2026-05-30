import { memo, useState } from 'react';
import './ChatArea.css';

const ThinkingSteps = memo(({ steps }) => {
  const [expanded, setExpanded] = useState(false);

  if (!steps || steps.length === 0) return null;

  const hasActiveStep = steps.some((s) => s.status === 'started');

  return (
    <div className="thinking-steps">
      <div
        className="thinking-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="thinking-toggle">{expanded ? '▼' : '▶'}</span>
        <span className="thinking-label">
          {hasActiveStep ? '思考中...' : '思考过程'}
        </span>
        <span className="thinking-count">{steps.length} 步</span>
      </div>
      {expanded && (
        <div className="thinking-body">
          {steps.map((step, idx) => (
            <div key={step.step} className={`thinking-step ${step.status}`}>
              <span className="step-icon">{step.icon}</span>
              <span className="step-label">{step.label}</span>
              {step.status === 'started' && (
                <span className="step-spinner" />
              )}
              {step.status === 'completed' && step.detail && (
                <span className="step-detail">{step.detail}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

ThinkingSteps.displayName = 'ThinkingSteps';

export const ChatArea = memo((props) => {
  const { messages, loading } = props;

  return (
    <div className="chat-area">
      {messages.map((msg, index) => (
        <div key={msg.id || index} className={`message-wrapper ${msg.type}`}>
          <div className={`message ${msg.type}`}>
            {msg.type === 'bot' && <div className="message-avatar">🤖</div>}
            <div className="message-content">
              {msg.type === 'bot' && msg.steps && msg.steps.length > 0 && (
                <ThinkingSteps steps={msg.steps} />
              )}
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
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="messages-end-ref" />
    </div>
  );
});

ChatArea.displayName = 'ChatArea';
