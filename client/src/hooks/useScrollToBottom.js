import { useEffect, useRef } from 'react';

/**
 * 自定义 Hook - 滚动到底部
 * @description 自动滚动容器到最新内容位置，适用于聊天消息、列表等场景
 * @param {Array} deps - 依赖数组，当变化时触发滚动
 * @returns {React.RefObject} containerRef - 容器引用，需绑定到目标 DOM 元素
 *
 * @example
 * ```jsx
 * const ChatMessages = ({ messages }) => {
 *   const containerRef = useScrollToBottom([messages]);
 *   return (
 *     <div ref={containerRef}>
 *       {messages.map(m => <Message key={m.id} {...m} />)}
 *     </div>
 *   );
 * };
 * ```
 */
const useScrollToBottom = (deps) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [deps]);

  return containerRef;
};

export default useScrollToBottom;