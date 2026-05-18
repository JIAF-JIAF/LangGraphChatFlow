"""
Skill 配置 API

提供 Skill 文件的上传、删除和列表查询接口。
"""

import os
import glob
from flask import Blueprint, request, jsonify
from modules.skill import SkillManager

skill_config_bp = Blueprint('skill_config', __name__, url_prefix='/api/skills')

SKILLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'skills'
)


@skill_config_bp.route('/', methods=['GET'])
def get_skills():
    """
    获取所有 Skill 列表
    
    Returns:
        JSON 响应，包含 Skill 列表和数量
    """
    try:
        skill_manager = SkillManager()
        skills = skill_manager.get_all_skills()
        
        skill_list = []
        for skill in skills:
            skill_list.append({
                "id": hash(skill.get('name', skill.get('title', ''))),
                "name": skill.get('name', ''),
                "title": skill.get('title', ''),
                "description": skill.get('description', ''),
                "file": f"{skill.get('name', '')}.skill.md",
                "trigger_keywords": skill.get('trigger_keywords', []),
                "updated": ""
            })
        
        return jsonify({
            "status": "success",
            "data": skill_list,
            "count": len(skill_list)
        })
    except Exception as e:
        print(f"获取 Skill 列表失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@skill_config_bp.route('/<skill_name>', methods=['GET'])
def get_skill(skill_name):
    """
    获取单个 Skill 详情
    
    Args:
        skill_name: Skill 名称
    
    Returns:
        JSON 响应，包含 Skill 详情或错误信息
    """
    try:
        skill_manager = SkillManager()
        skill = skill_manager.get_skill(skill_name)
        
        if skill:
            return jsonify({
                "status": "success",
                "data": skill
            })
        return jsonify({
            "status": "error",
            "message": "Skill 不存在"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@skill_config_bp.route('/upload', methods=['POST'])
def upload_skill():
    """
    上传 Skill 文件
    
    Request Body:
        multipart/form-data 格式，包含 file 字段
    
    Returns:
        JSON 响应，包含上传结果
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "缺少文件"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "请选择文件"
            }), 400
        
        if not file.filename.endswith('.skill.md'):
            return jsonify({
                "status": "error",
                "message": "文件格式不正确，请上传 .skill.md 文件"
            }), 400
        
        file_path = os.path.join(SKILLS_DIR, file.filename)
        file.save(file_path)
        
        return jsonify({
            "status": "success",
            "message": "Skill 上传成功",
            "data": {
                "filename": file.filename,
                "path": file_path
            }
        }), 201
    except Exception as e:
        print(f"上传 Skill 失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@skill_config_bp.route('/<skill_name>', methods=['DELETE'])
def delete_skill(skill_name):
    """
    删除 Skill 文件
    
    Args:
        skill_name: Skill 名称（不含 .skill.md 扩展名）
    
    Returns:
        JSON 响应，包含删除结果
    """
    try:
        filename = f"{skill_name}.skill.md"
        file_path = os.path.join(SKILLS_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "Skill 不存在"
            }), 404
        
        os.remove(file_path)
        
        return jsonify({
            "status": "success",
            "message": "Skill 删除成功"
        })
    except Exception as e:
        print(f"删除 Skill 失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@skill_config_bp.route('/reload', methods=['POST'])
def reload_skills():
    """
    重新加载所有 Skill
    
    重新从磁盘读取所有 .skill.md 文件
    
    Returns:
        JSON 响应，包含重新加载结果和 Skill 数量
    """
    try:
        skill_manager = SkillManager()
        skill_manager.load_skills()
        
        return jsonify({
            "status": "success",
            "message": "Skill 重新加载成功",
            "count": len(skill_manager.get_all_skills())
        })
    except Exception as e:
        print(f"重新加载 Skill 失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
