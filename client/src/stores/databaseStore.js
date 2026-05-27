import { create } from 'zustand';
import vectorDbApi from '../api/vectorDb';
import { ALLOWED_EXTENSIONS } from '../constants/fileExtensions';

/**
 * 数据库信息类型定义
 * @typedef {Object} Database
 * @property {string} name - 数据库名称
 * @property {number} document_count - 文档数量
 * @property {number} vector_count - 向量数量
 * @property {string} [description] - 数据库描述
 */

/**
 * 文档信息类型定义
 * @typedef {Object} Document
 * @property {string} filename - 文件名
 * @property {number} chunk_count - 分块数量
 * @property {number} vector_count - 向量数量
 */

/**
 * 向量数据库状态管理 Store
 * @description 管理数据库列表、文档、文件上传等操作
 *
 * @returns {Object} 数据库状态和方法
 *
 * @example
 * ```jsx
 * const { databases, selectedDb, loadDatabases } = useDatabaseStore();
 * await loadDatabases();
 * ```
 */
const useDatabaseStore = create((set, get) => ({
  /**
   * 数据库列表
   * @type {Database[]}
   */
  databases: [],

  /**
   * 当前选中的数据库
   * @type {Database|null}
   */
  selectedDb: null,

  /**
   * 当前数据库的文档列表
   * @type {Document[]}
   */
  documents: [],

  /**
   * 加载状态
   * @type {boolean}
   */
  loading: false,

  /**
   * 上传状态
   * @type {boolean}
   */
  uploading: false,

  /**
   * 上传进度 (0-100)
   * @type {number}
   */
  uploadProgress: 0,

  /**
   * 提示消息
   * @type {string}
   */
  message: '',

  /**
   * 消息类型
   * @type {'success'|'error'|'warning'}
   */
  messageType: 'success',

  /**
   * 显示提示消息
   * @param {string} msg - 消息内容
   * @param {'success'|'error'|'warning'} [type='success'] - 消息类型
   */
  showMessage: (msg, type = 'success') => {
    set({ message: msg, messageType: type });
    setTimeout(() => set({ message: '' }), 3000);
  },

  /**
   * 加载数据库列表
   * @returns {Promise<void>}
   */
  loadDatabases: async () => {
    set({ loading: true });
    try {
      const response = await vectorDbApi.getDatabases();
      if (response.status === 'success') {
        const databases = response.data;
        set({ databases });
        if (!get().selectedDb && databases.length > 0) {
          set({ selectedDb: databases[0] });
        }
      }
    } catch (error) {
      console.error('加载数据库失败:', error);
      get().showMessage('加载数据库失败', 'error');
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 加载指定数据库的文档列表
   * @param {string} dbName - 数据库名称
   * @returns {Promise<void>}
   */
  loadDocuments: async (dbName) => {
    try {
      const response = await vectorDbApi.getDocuments(dbName);
      if (response.status === 'success') {
        set({ documents: response.data });
      } else {
        set({ documents: [] });
      }
    } catch (error) {
      console.error('加载文档列表失败:', error);
      set({ documents: [] });
    }
  },

  /**
   * 选择数据库
   * @param {Database|null} db - 数据库对象
   */
  selectDatabase: (db) => {
    set({ selectedDb: db });
    if (db) {
      get().loadDocuments(db.name);
    } else {
      set({ documents: [] });
    }
  },

  /**
   * 创建数据库
   * @param {string} name - 数据库名称
   * @param {string} [description] - 数据库描述
   * @returns {Promise<boolean>} 是否创建成功
   */
  createDatabase: async (name, description) => {
    try {
      const response = await vectorDbApi.createDatabase(name, description);
      if (response.status === 'success') {
        get().showMessage(response.message, 'success');
        await get().loadDatabases();
        return true;
      } else {
        get().showMessage(response.message, 'error');
        return false;
      }
    } catch (error) {
      get().showMessage('创建数据库失败', 'error');
      return false;
    }
  },

  /**
   * 删除数据库
   * @param {string} dbName - 数据库名称
   * @returns {Promise<boolean>} 是否删除成功
   */
  deleteDatabase: async (dbName) => {
    try {
      const response = await vectorDbApi.deleteDatabase(dbName);
      if (response.status === 'success') {
        get().showMessage(response.message, 'success');
        await get().loadDatabases();
        if (get().selectedDb?.name === dbName) {
          set({ selectedDb: null, documents: [] });
        }
        return true;
      } else {
        get().showMessage(response.message, 'error');
        return false;
      }
    } catch (error) {
      get().showMessage('删除数据库失败', 'error');
      return false;
    }
  },

  /**
   * 上传文件到当前数据库
   * @param {FileList|File[]} files - 文件列表
   * @returns {Promise<boolean>} 是否上传成功
   */
  uploadFiles: async (files) => {
    const { selectedDb, showMessage, loadDatabases, loadDocuments } = get();
    if (!selectedDb) {
      showMessage('请先选择一个数据库', 'warning');
      return false;
    }

    const validFiles = Array.from(files).filter((file) => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      return ALLOWED_EXTENSIONS.includes(ext);
    });

    if (validFiles.length === 0) {
      showMessage('没有有效的文件，请上传 TXT、PDF、MD、CSV、DOCX、XLSX 或 XLS 文件', 'error');
      return false;
    }

    set({ uploading: true, uploadProgress: 0 });

    try {
      const progressInterval = setInterval(() => {
        set((state) => {
          if (state.uploadProgress >= 50) {
            clearInterval(progressInterval);
            return { uploadProgress: 50 };
          }
          return { uploadProgress: state.uploadProgress + 10 };
        });
      }, 200);

      const response = await vectorDbApi.uploadFiles(selectedDb.name, validFiles);
      clearInterval(progressInterval);
      set({ uploadProgress: 100 });

      if (response.status === 'success') {
        showMessage(response.message, 'success');
        await loadDatabases();
        await loadDocuments(selectedDb.name);
        set((state) => ({
          selectedDb: {
            ...state.selectedDb,
            document_count: state.selectedDb.document_count + validFiles.length,
            vector_count: response.data.vector_count
          }
        }));
        return true;
      } else {
        showMessage(response.message, 'error');
        return false;
      }
    } catch (error) {
      console.error('上传文件失败:', error);
      showMessage('上传文件失败', 'error');
      return false;
    } finally {
      set({ uploading: false, uploadProgress: 0 });
    }
  },

  /**
   * 删除文档
   * @param {string} docName - 文档名称
   * @returns {Promise<boolean>} 是否删除成功
   */
  deleteDocument: async (docName) => {
    const { selectedDb, loadDocuments, showMessage } = get();
    if (!selectedDb) return false;

    try {
      const response = await vectorDbApi.deleteDocument(selectedDb.name, docName);
      if (response.status === 'success') {
        showMessage(response.message, 'success');
        await loadDocuments(selectedDb.name);
        set((state) => ({
          selectedDb: {
            ...state.selectedDb,
            document_count: Math.max(0, state.selectedDb.document_count - 1),
            vector_count: response.data.vector_count
          }
        }));
        return true;
      } else {
        showMessage(response.message, 'error');
        return false;
      }
    } catch (error) {
      showMessage('删除文档失败', 'error');
      return false;
    }
  }
}));

export default useDatabaseStore;