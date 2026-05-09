"""
智能客服 Agent 主应用
Flask Web 服务入口
LangGraph 版本（渐进式迁移）
"""

import uuid
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from modules.ai_client import AIClient
from modules.rag import RAGChain
from modules.assistant import Agent as LangChainAgent
from modules.langgraph import LangGraphAgent
from modules.prompt import create_few_shot_prompt
from modules.rate_limit import RateLimiter
from mcp_module import MCPToolService, config

if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    import codecs
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ['PYTHONIOENCODING'] = 'utf-8'

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
CORS(app)

rate_limiter = RateLimiter(config_path="config.json")
rate_limiter.init_app(app)

assistant_instance = None
rag_chain_instance = None
sessions = {}


def init_system():
    """初始化系统组件。

    按顺序初始化 AI 客户端、知识库和 AI 助手，
    确保所有组件正常启动后提供服务。
    """
    global assistant_instance, rag_chain_instance

    print("=" * 50)
    print("智能客服系统启动中... (LangGraph 版本 - 渐进式迁移)")
    print("=" * 50)

    print("\n[1/3] 初始化 AI 客户端...")
    try:
        ai_client = AIClient(config_path="config.json")
        print("AI 客户端初始化完成")
    except Exception as e:
        print("AI 客户端初始化失败: {}".format(e))
        raise

    print("\n[2/3] 初始化 RAG 知识库...")
    try:
        # 创建模块化 RAG 链
        rag_chain_instance = RAGChain()
        rag_chain_instance.init_default_modules(ai_client)
        
        # 构建知识库索引
        kb_data = rag_chain_instance.build_index()
        if kb_data["status"] == "error":
            print(f"知识库加载失败: {kb_data.get('message', '未知错误')}")
        elif kb_data["status"] == "empty":
            print("知识库为空，将跳过 RAG 检索")
        else:
            print(f"知识库初始化完成，共 {kb_data['count']} 个向量")
    except Exception as e:
        print("知识库初始化警告: {}".format(e))

    print("\n[3/3] 初始化 AI 助手...")
    try:
        # 从配置的所有启用 MCP 服务器获取工具
        # 支持多个 MCP 服务器配置，自动合并所有服务器的工具
        tools = MCPToolService.get_tools()

        # 创建 LangChain Agent（原有实现）
        langchain_agent = LangChainAgent(options={
            "prompt": create_few_shot_prompt(),  # 使用默认示例
            "ragChain": rag_chain_instance,
            "tools": tools,
            "aiClient": ai_client
        })
        
        # 将 LangChain Agent 封装到 LangGraphAgent 中（渐进式迁移）
        assistant_instance = LangGraphAgent(langchain_agent=langchain_agent)
        
        print("AI 助手初始化完成 (LangGraph 封装模式)")
    except Exception as e:
        print("AI 助手初始化失败: {}".format(e))
        raise

    print("\n" + "=" * 50)
    print("智能客服系统就绪!")
    print("=" * 50)
    print("\n服务地址: http://localhost:5000")
    print("API 文档:")
    print("  GET  /start  - 检查服务状态")
    print("  POST /chat   - 发送对话请求")
    print("=" * 50 + "\n")


@app.route('/start', methods=['GET'])
@rate_limiter.limit("start_limit")
def start():
    """检查服务状态。

    返回服务是否就绪，以及知识库初始化状态。

    Returns:
        JSON 响应，包含 status、message、model 和 knowledge_base 字段
    """
    try:
        status = {
            "status": "ready",
            "message": "客服系统已就绪 (LangGraph - 渐进式迁移)",
            "model": "deepseek-v4-pro",
            "knowledge_base": rag_chain_instance is not None
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/chat', methods=['POST'])
@rate_limiter.limit("chat_limit")
def chat():
    """处理对话请求。

    接收用户消息，调用 Agent 处理并返回回复。

    Request Body:
        message (str): 用户输入的消息内容
        session_id (str, optional): 会话 ID，默认自动生成

    Returns:
        JSON 响应，包含 reply、tool_calls、session_id 和 finished 字段
    """
    try:
        print("\n[DEBUG] /chat 路由被调用", flush=True)
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "缺少 message 字段"
            }), 400

        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))

        print("\n[对话请求] Session: {}".format(session_id), flush=True)
        print("用户: {}".format(user_message), flush=True)

        result = assistant_instance.process_message(session_id, user_message)

        response = {
            "reply": result.get("content", ""),
            "tool_calls": result.get("tool_calls", []),
            "session_id": session_id,
            "finished": False
        }

        return jsonify(response)

    except Exception as e:
        print("对话处理异常: {}".format(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "请求过于频繁，请稍后再试",
        "message": str(e.description)
    }), 429


if __name__ == '__main__':
    init_system()
    app.run(host='0.0.0.0', port=5000, debug=True)
