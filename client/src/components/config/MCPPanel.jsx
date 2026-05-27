import { memo } from 'react';
import useConfigStore from '../../stores/configStore';

/**
 * MCP 配置面板组件
 * @description 管理和添加 MCP 服务器配置
 *
 * @returns {React.ReactElement}
 */
export const MCPPanel = memo(() => {
  const {
    mcpServers,
    mcpLoading,
    mcpForm,
    setMcpForm,
    addMcpServer,
    deleteMcpServer
  } = useConfigStore();

  /**
   * 处理添加服务器
   * @returns {Promise<void>}
   */
  const handleAddServer = async () => {
    await addMcpServer();
  };

  /**
   * 处理删除服务器
   * @param {number} id - 服务器 ID
   * @returns {Promise<void>}
   */
  const handleDeleteServer = async (id) => {
    if (!window.confirm('确定要删除这个 MCP Server 吗？')) {
      return;
    }
    await deleteMcpServer(id);
  };

  return (
    <div className="mcp-content">
      <div className="section-card">
        <div className="section-header">
          <h3>添加 MCP Server</h3>
        </div>
        <div className="mcp-form">
          <input
            type="text"
            value={mcpForm.name}
            onChange={(e) => setMcpForm('name', e.target.value)}
            placeholder="服务器名称"
          />
          <select
            value={mcpForm.protocol}
            onChange={(e) => setMcpForm('protocol', e.target.value)}
          >
            <option value="StreamableHTTP">Streamable HTTP</option>
            <option value="HTTP" disabled>
              HTTP (暂不可用)
            </option>
            <option value="WebSocket" disabled>
              WebSocket (暂不可用)
            </option>
          </select>
          <input
            type="text"
            value={mcpForm.url}
            onChange={(e) => setMcpForm('url', e.target.value)}
            placeholder="输入 MCP Server URL"
          />
          <input
            type="text"
            value={mcpForm.description}
            onChange={(e) => setMcpForm('description', e.target.value)}
            placeholder="描述（可选）"
          />
          <button className="btn btn-primary" onClick={handleAddServer}>
            确认添加
          </button>
        </div>
      </div>

      <div className="section-card">
        <div className="section-header">
          <h3>MCP 服务器列表</h3>
        </div>
        {mcpLoading ? (
          <div className="empty-state">
            <div className="spinner"></div>
            <span>加载中...</span>
          </div>
        ) : mcpServers.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">🔌</span>
            <p>暂无 MCP 配置</p>
            <p className="empty-hint">添加服务器即可连接</p>
          </div>
        ) : (
          <div className="mcp-list">
            {mcpServers.map((server) => (
              <div key={server.id} className="mcp-item">
                <div className="mcp-info">
                  <div className="mcp-header">
                    <span className="mcp-name">{server.name || '未命名服务器'}</span>
                    <span className={`mcp-status ${server.status}`}>
                      {server.status === 'connected' ? '已连接' : '未连接'}
                    </span>
                  </div>
                  <span className="mcp-url">{server.url}</span>
                  <div className="mcp-meta">
                    <span className="mcp-protocol">{server.protocol}</span>
                    {server.description && (
                      <span className="mcp-description">{server.description}</span>
                    )}
                  </div>
                </div>
                <button
                  className="mcp-delete"
                  onClick={() => handleDeleteServer(server.id)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
});

MCPPanel.displayName = 'MCPPanel';