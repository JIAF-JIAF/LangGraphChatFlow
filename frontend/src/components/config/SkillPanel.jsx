import { memo } from 'react';
import useConfigStore from '../../stores/configStore';

/**
 * Skill 配置面板组件
 * @description 管理和安装 Skill 技能扩展
 *
 * @returns {React.ReactElement}
 */
export const SkillPanel = memo(() => {
  const {
    skills,
    skillLoading,
    skillUrl,
    skillInstalling,
    setSkillUrl,
    installSkill,
    deleteSkill
  } = useConfigStore();

  /**
   * 处理安装 Skill
   * @returns {Promise<void>}
   */
  const handleInstall = async () => {
    await installSkill();
  };

  /**
   * 处理删除 Skill
   * @param {string} skillName - Skill 名称
   * @returns {Promise<void>}
   */
  const handleDelete = async (skillName) => {
    if (!window.confirm('确定要删除这个 Skill 吗？')) {
      return;
    }
    await deleteSkill(skillName);
  };

  return (
    <div className="skill-content">
      <div className="section-card">
        <div className="section-header">
          <h3>安装 Skill</h3>
        </div>
        <div className="skill-install-form">
          <input
            type="text"
            value={skillUrl}
            onChange={(e) => setSkillUrl(e.target.value)}
            placeholder="输入 Skill Git 地址"
            disabled={skillInstalling}
          />
          <button
            className="btn btn-primary"
            onClick={handleInstall}
            disabled={skillInstalling}
          >
            {skillInstalling ? (
              <>
                <div className="spinner-small"></div>
                <span>安装中...</span>
              </>
            ) : (
              '安装'
            )}
          </button>
        </div>
      </div>

      <div className="section-card">
        <div className="section-header">
          <h3>Skill 列表</h3>
        </div>
        {skillLoading ? (
          <div className="empty-state">
            <div className="spinner"></div>
            <span>加载中...</span>
          </div>
        ) : skills.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">⚡</span>
            <p>暂无 Skill</p>
            <p className="empty-hint">输入 Git 地址安装技能</p>
          </div>
        ) : (
          <div className="skill-list">
            {skills.map((skill) => (
              <div key={skill.id} className="skill-item">
                <div className="skill-info">
                  <span className="skill-name">{skill.title}</span>
                  <span className="skill-meta">
                    {skill.file} · 更新于 {skill.updated}
                  </span>
                </div>
                <button
                  className="skill-delete"
                  onClick={() => handleDelete(skill.name)}
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

SkillPanel.displayName = 'SkillPanel';