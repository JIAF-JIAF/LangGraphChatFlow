import { memo } from 'react';
import useDatabaseStore from '../../stores/databaseStore';
import useUiStore from '../../stores/uiStore';

/**
 * 创建数据库模态框组件
 * @description 用于新建向量数据库的弹窗表单
 *
 * @returns {React.ReactElement|null}
 */
export const CreateDatabaseModal = memo((props) => {
  const { showCreateModal, closeCreateModal, newDbForm, setNewDbForm } = useUiStore();
  const { createDatabase } = useDatabaseStore();

  /**
   * 处理创建数据库
   * @returns {Promise<void>}
   */
  const handleCreate = async () => {
    const nameRegex = /^[a-zA-Z0-9][a-zA-Z0-9-_.]{2,511}$/;
    if (!newDbForm.name.trim()) {
      useDatabaseStore.getState().showMessage('请输入数据库名称', 'warning');
      return;
    }
    if (!nameRegex.test(newDbForm.name.trim())) {
      useDatabaseStore.getState().showMessage('数据库名称格式不正确', 'warning');
      return;
    }
    const success = await createDatabase(newDbForm.name.trim(), newDbForm.description.trim());
    if (success) {
      closeCreateModal();
    }
  };

  if (!showCreateModal) return null;

  return (
    <div className="modal-overlay" onClick={closeCreateModal}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>新建数据库</h3>
          <button className="modal-close" onClick={closeCreateModal}>
            ✕
          </button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>数据库名称</label>
            <input
              type="text"
              value={newDbForm.name}
              onChange={(e) => setNewDbForm('name', e.target.value)}
              placeholder="请输入数据库名称"
            />
            <p className="form-hint">
              名称只能包含英文、数字、下划线(_)和连字符(-)，长度3-512个字符
            </p>
          </div>
          <div className="form-group">
            <label>描述（可选）</label>
            <textarea
              value={newDbForm.description}
              onChange={(e) => setNewDbForm('description', e.target.value)}
              placeholder="请输入数据库描述"
              rows={3}
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={closeCreateModal}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleCreate}>
            创建
          </button>
        </div>
      </div>
    </div>
  );
});

CreateDatabaseModal.displayName = 'CreateDatabaseModal';