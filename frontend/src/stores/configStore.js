import { create } from 'zustand';
import mcpConfigApi from '../api/mcpConfig';
import skillConfigApi from '../api/skillConfig';

/**
 * MCP 服务器信息类型定义
 * @typedef {Object} MCPServer
 * @property {number} id - 服务器 ID
 * @property {string} name - 服务器名称
 * @property {string} url - 服务器地址
 * @property {string} protocol - 协议类型
 * @property {string} status - 连接状态
 * @property {string} [description] - 服务器描述
 */

/**
 * Skill 信息类型定义
 * @typedef {Object} Skill
 * @property {number} id - Skill ID
 * @property {string} name - Skill 名称
 * @property {string} title - 显示标题
 * @property {string} file - 文件路径
 * @property {string} updated - 更新日期
 */

/**
 * MCP 和 Skill 配置状态管理 Store
 * @description 管理 MCP 服务器和 Skill 的增删改查操作
 *
 * @returns {Object} 配置状态和方法
 *
 * @example
 * ```jsx
 * const { mcpServers, loadMcpServers, addMcpServer } = useConfigStore();
 * await loadMcpServers();
 * ```
 */
const useConfigStore = create((set, get) => ({
  /**
   * MCP 服务器列表
   * @type {MCPServer[]}
   */
  mcpServers: [],

  /**
   * MCP 加载状态
   * @type {boolean}
   */
  mcpLoading: false,

  /**
   * MCP 表单数据
   * @type {{ name: string, url: string, description: string, protocol: string }}
   */
  mcpForm: {
    name: '',
    url: '',
    description: '',
    protocol: 'StreamableHTTP'
  },

  /**
   * Skill 列表
   * @type {Skill[]}
   */
  skills: [],

  /**
   * Skill 加载状态
   * @type {boolean}
   */
  skillLoading: false,

  /**
   * Skill 安装 URL 输入
   * @type {string}
   */
  skillUrl: '',

  /**
   * Skill 安装中状态
   * @type {boolean}
   */
  skillInstalling: false,

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
   * 加载 MCP 服务器列表
   * @returns {Promise<void>}
   */
  loadMcpServers: async () => {
    set({ mcpLoading: true });
    try {
      const response = await mcpConfigApi.getServers();
      if (response.status === 'success') {
        set({ mcpServers: response.data });
      } else {
        set({ mcpServers: [] });
      }
    } catch (error) {
      console.error('加载 MCP 服务器失败:', error);
      set({ mcpServers: [] });
    } finally {
      set({ mcpLoading: false });
    }
  },

  /**
   * 更新 MCP 表单字段
   * @param {string} field - 字段名
   * @param {string} value - 字段值
   */
  setMcpForm: (field, value) => {
    set((state) => ({
      mcpForm: { ...state.mcpForm, [field]: value }
    }));
  },

  /**
   * 重置 MCP 表单
   */
  resetMcpForm: () => {
    set({
      mcpForm: {
        name: '',
        url: '',
        description: '',
        protocol: 'StreamableHTTP'
      }
    });
  },

  /**
   * 添加 MCP 服务器
   * @returns {Promise<boolean>} 是否添加成功
   */
  addMcpServer: async () => {
    const { mcpForm, mcpServers, showMessage, loadMcpServers } = get();

    if (!mcpForm.name.trim()) {
      showMessage('请输入服务器名称', 'warning');
      return false;
    }
    if (!mcpForm.url.trim()) {
      showMessage('请输入 MCP Server URL', 'warning');
      return false;
    }

    try {
      const response = await mcpConfigApi.addServer({
        name: mcpForm.name.trim(),
        url: mcpForm.url.trim(),
        protocol: mcpForm.protocol,
        description: mcpForm.description.trim()
      });

      if (response.status === 'success') {
        set({ mcpServers: [...mcpServers, response.data] });
        get().resetMcpForm();
        showMessage('MCP Server 添加成功', 'success');
        return true;
      } else {
        showMessage(response.message || '添加失败', 'error');
        return false;
      }
    } catch (error) {
      console.error('添加 MCP Server 失败:', error);
      showMessage('添加 MCP Server 失败', 'error');
      return false;
    }
  },

  /**
   * 删除 MCP 服务器
   * @param {number} id - 服务器 ID
   * @returns {Promise<boolean>} 是否删除成功
   */
  deleteMcpServer: async (id) => {
    try {
      const response = await mcpConfigApi.deleteServer(id);
      if (response.status === 'success') {
        set((state) => ({
          mcpServers: state.mcpServers.filter((server) => server.id !== id)
        }));
        get().showMessage('MCP Server 删除成功', 'success');
        return true;
      } else {
        get().showMessage(response.message || '删除失败', 'error');
        return false;
      }
    } catch (error) {
      console.error('删除 MCP Server 失败:', error);
      get().showMessage('删除 MCP Server 失败', 'error');
      return false;
    }
  },

  /**
   * 加载 Skill 列表
   * @returns {Promise<void>}
   */
  loadSkills: async () => {
    set({ skillLoading: true });
    try {
      const response = await skillConfigApi.getSkills();
      if (response.status === 'success') {
        const formattedSkills = response.data.map((skill) => {
          let updated = '未知';
          if (skill.updated) {
            if (typeof skill.updated === 'string') {
              updated = skill.updated.split(' ')[0];
            } else {
              updated = new Date(skill.updated * 1000).toISOString().split('T')[0];
            }
          }
          return { ...skill, updated };
        });
        set({ skills: formattedSkills });
      } else {
        set({ skills: [] });
      }
    } catch (error) {
      console.error('加载 Skill 列表失败:', error);
      set({ skills: [] });
    } finally {
      set({ skillLoading: false });
    }
  },

  /**
   * 设置 Skill 安装 URL
   * @param {string} url - Git 仓库地址
   */
  setSkillUrl: (url) => set({ skillUrl: url }),

  /**
   * 安装 Skill
   * @returns {Promise<boolean>} 是否安装成功
   */
  installSkill: async () => {
    const { skillUrl, showMessage, loadSkills } = get();

    if (!skillUrl.trim()) {
      showMessage('请输入 Skill Git 地址', 'warning');
      return false;
    }

    set({ skillInstalling: true });
    try {
      const response = await skillConfigApi.installFromUrl(skillUrl.trim());
      if (response.status === 'success') {
        showMessage('Skill 安装成功', 'success');
        set({ skillUrl: '' });
        await loadSkills();
        return true;
      } else {
        showMessage(response.message || '安装失败', 'error');
        return false;
      }
    } catch (error) {
      console.error('安装 Skill 失败:', error);
      showMessage('安装 Skill 失败', 'error');
      return false;
    } finally {
      set({ skillInstalling: false });
    }
  },

  /**
   * 删除 Skill
   * @param {string} skillName - Skill 名称
   * @returns {Promise<boolean>} 是否删除成功
   */
  deleteSkill: async (skillName) => {
    try {
      const response = await skillConfigApi.uninstall(skillName);
      if (response.status === 'success') {
        set((state) => ({
          skills: state.skills.filter((skill) => skill.name !== skillName)
        }));
        get().showMessage('Skill 删除成功', 'success');
        return true;
      } else {
        get().showMessage(response.message || '删除失败', 'error');
        return false;
      }
    } catch (error) {
      console.error('删除 Skill 失败:', error);
      get().showMessage('删除 Skill 失败', 'error');
      return false;
    }
  },

  /**
   * 加载所有配置数据
   * @description 同时加载 MCP 服务器和 Skill 列表
   * @returns {Promise<void>}
   */
  loadAll: async () => {
    await Promise.all([get().loadMcpServers(), get().loadSkills()]);
  }
}));

export default useConfigStore;