import { useEffect, memo } from 'react';
import useDatabaseStore from '../../stores/databaseStore';
import useUiStore from '../../stores/uiStore';
import useConfigStore from '../../stores/configStore';

/**
 * 配置侧边栏组件
 * @description 左侧导航栏，显示 Agent 配置中心 Logo、标签页切换和数据库列表
 *
 * @returns {React.ReactElement}
 */
export const Sidebar = memo(() => {
  const { databases, selectedDb, loading, selectDatabase, deleteDatabase } = useDatabaseStore();
  const { openCreateModal } = useUiStore();
  const { loadAll } = useConfigStore();

  /**
   * 组件挂载时加载所有数据
   */
  useEffect(() => {
    loadAll();
  }, [loadAll]);

  /**
   * 处理删除数据库
   * @param {MouseEvent} e - 点击事件
   * @param {string} dbName - 数据库名称
   * @returns {Promise<void>}
   */
  const handleDeleteDb = async (e, dbName) => {
    e.stopPropagation();
    if (!window.confirm(`确定要删除数据库 "${dbName}" 及其所有内容吗？`)) {
      return;
    }
    await deleteDatabase(dbName);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <span className="logo-text">Agent 配置中心</span>
        </div>
      </div>
      <div className="db-section">
        <h3>数据库列表</h3>
        <button className="btn btn-primary btn-new-db" onClick={openCreateModal}>
          + 新建数据库
        </button>
        <div className="db-list">
          {loading ? (
            <div className="empty-state">
              <div className="spinner"></div>
              <span>加载中...</span>
            </div>
          ) : databases.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📚</span>
              <p>暂无数据库</p>
            </div>
          ) : (
            databases.map((db) => (
              <div
                key={db.name}
                className={`db-item ${selectedDb?.name === db.name ? 'selected' : ''}`}
                onClick={() => selectDatabase(db)}
              >
                <div className="db-info">
                  <div className="db-name">{db.name}</div>
                  <div className="db-meta">
                    <span>{db.document_count} 文档</span>
                    <span>·</span>
                    <span>{db.vector_count} 向量</span>
                  </div>
                </div>
                <button className="btn-delete" onClick={(e) => handleDeleteDb(e, db.name)}>
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
});

Sidebar.displayName = 'Sidebar';