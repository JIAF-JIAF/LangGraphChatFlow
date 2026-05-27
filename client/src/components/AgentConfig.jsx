import { useEffect, memo } from 'react';
import useDatabaseStore from '../stores/databaseStore';
import useUiStore from '../stores/uiStore';
import { Sidebar } from './config/Sidebar';
import { DatabasePanel } from './config/DatabasePanel';
import { MCPPanel } from './config/MCPPanel';
import { SkillPanel } from './config/SkillPanel';
import { CreateDatabaseModal } from './config/CreateDatabaseModal';
import { FilePreview } from '../preview';
import './AgentConfig.css';

export const AgentConfig = memo((props) => {
  const { activeTab, setActiveTab, showPreviewSidebar } = useUiStore();
  const { databases, message, messageType, loadDatabases } = useDatabaseStore();

  const tabs = [
    { id: 'database', label: '数据库', icon: '📊' },
    { id: 'mcp', label: 'MCP 配置', icon: '🔌' },
    { id: 'skill', label: 'Skill', icon: '⚡' }
  ];

  useEffect(() => {
    loadDatabases();
  }, [loadDatabases]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'database':
        return <DatabasePanel />;
      case 'mcp':
        return <MCPPanel />;
      case 'skill':
        return <SkillPanel />;
      default:
        return <DatabasePanel />;
    }
  };

  return (
    <div className="agent-config">
      {message && (
        <div className={`message message-${messageType}`}>{message}</div>
      )}

      <div className="main-content">
        <Sidebar />

        <div className={`content ${showPreviewSidebar ? 'content-shrink' : ''}`}>
          <div className="content-header">
            <div className="tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span className="tab-icon">{tab.icon}</span>
                  <span className="tab-label">{tab.label}</span>
                </button>
              ))}
            </div>
            <div className="stats-bar">
              <span className="stat-item">数据库: {databases.length}</span>
              <span className="stat-divider">|</span>
              <span className="stat-item">
                文档总数:{' '}
                {databases.reduce((sum, db) => sum + db.document_count, 0)}
              </span>
            </div>
          </div>

          <div className="tab-content">{renderTabContent()}</div>
        </div>

        {showPreviewSidebar && <FilePreview />}
      </div>

      <CreateDatabaseModal />
    </div>
  );
});

AgentConfig.displayName = 'AgentConfig';