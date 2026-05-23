import { create } from 'zustand';

/**
 * UI 状态管理 Store
 * @description 管理 UI 状态，如标签页、模态框、表单等
 *
 * @returns {Object} UI 状态和方法
 *
 * @example
 * ```jsx
 * const { activeTab, setActiveTab, openCreateModal } = useUiStore();
 * setActiveTab('mcp');
 * ```
 */
const useUiStore = create((set) => ({
  /**
   * 当前激活的标签页
   * @type {'database'|'mcp'|'skill'}
   */
  activeTab: 'database',

  /**
   * 是否显示创建数据库模态框
   * @type {boolean}
   */
  showCreateModal: false,

  /**
   * 新建数据库表单
   * @type {{ name: string, description: string }}
   */
  newDbForm: {
    name: '',
    description: ''
  },

  /**
   * 设置当前激活的标签页
   * @param {'database'|'mcp'|'skill'} tab - 标签页 ID
   */
  setActiveTab: (tab) => set({ activeTab: tab }),

  /**
   * 打开创建数据库模态框
   */
  openCreateModal: () => set({ showCreateModal: true }),

  /**
   * 关闭创建数据库模态框并重置表单
   */
  closeCreateModal: () => set({
    showCreateModal: false,
    newDbForm: { name: '', description: '' }
  }),

  /**
   * 更新新建数据库表单字段
   * @param {string} field - 字段名
   * @param {string} value - 字段值
   */
  setNewDbForm: (field, value) => {
    set((state) => ({
      newDbForm: { ...state.newDbForm, [field]: value }
    }));
  },

  /**
   * 重置新建数据库表单
   */
  resetNewDbForm: () => set({
    newDbForm: { name: '', description: '' }
  })
}));

export default useUiStore;