import axios from 'axios';

/**
 * Skill 配置 API 客户端
 * 提供 Skill 文件的上传、删除和列表查询操作
 */
class SkillConfigApi {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || '/api';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 获取所有 Skill 列表
   * @returns {Promise<Object>} Skill 列表
   */
  async getSkills() {
    try {
      const response = await this.client.get('/api/skills');
      return response.data;
    } catch (error) {
      console.error('获取 Skill 列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取单个 Skill
   * @param {string} skillName - Skill 名称
   * @returns {Promise<Object>} Skill 详情
   */
  async getSkill(skillName) {
    try {
      const response = await this.client.get(`/api/skills/${skillName}`);
      return response.data;
    } catch (error) {
      console.error(`获取 Skill ${skillName} 失败:', error`);
      throw error;
    }
  }

  /**
   * 上传 Skill 文件
   * @param {File} file - Skill 文件 (.skill.md)
   * @returns {Promise<Object>} 上传结果
   */
  async uploadSkill(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await this.client.post('/api/skills/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('上传 Skill 失败:', error);
      throw error;
    }
  }

  /**
   * 删除 Skill
   * @param {string} skillName - Skill 名称
   * @returns {Promise<Object>} 删除结果
   */
  async deleteSkill(skillName) {
    try {
      const response = await this.client.delete(`/api/skills/${skillName}`);
      return response.data;
    } catch (error) {
      console.error(`删除 Skill ${skillName} 失败:', error`);
      throw error;
    }
  }

  /**
   * 重新加载所有 Skill
   * @returns {Promise<Object>} 重新加载结果
   */
  async reloadSkills() {
    try {
      const response = await this.client.post('/api/skills/reload');
      return response.data;
    } catch (error) {
      console.error('重新加载 Skill 失败:', error);
      throw error;
    }
  }
}

// 创建单例实例
const skillConfigApi = new SkillConfigApi();

export default skillConfigApi;
