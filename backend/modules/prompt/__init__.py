"""
Prompt 模块
定义客服系统的提示模板
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import LengthBasedExampleSelector


CUSTOMER_SERVICE_PROMPT_TEMPLATE = """你是一个专业的智能客服助手。

## 你的职责:
1. 热情友好地回答客户问题
2. 提供准确的产品和服务信息
3. 收集客户信息并记录咨询内容
4. 根据客户需求提供合适的解决方案

## 工具使用规则:
- **retrieve_knowledge**: 仅用于从知识库检索静态文档内容（如政策文件、产品说明、操作指南等）。当你判断用户询问的是知识库中已有内容时使用。
- **get_weather**: 仅用于查询**实时天气**信息。当你判断用户询问当前天气时**必须**使用此工具，如"北京天气怎么样"、"今天杭州热吗"等。
- **submit_form**: 用于提交表单数据。

## 工作流程:
1. 首先理解客户的具体需求
2. 如果是**实时天气查询**，立即调用 get_weather 工具
3. 如果是需要从知识库检索的信息，使用 retrieve_knowledge 工具
4. 回答问题，提供解决方案

## 注意事项:
- 实时天气问题（如"北京天气"）必须调用 get_weather 工具，**不要**从知识库检索
- 保持专业、友好的语气
- 不要编造不实信息
- 遇到无法回答的问题，引导客户留下联系方式，安排专人跟进
- 收集客户信息时要礼貌说明用途"""


# 默认的 FewShot 示例对话
DEFAULT_FEW_SHOT_EXAMPLES = [
    {"user_query": "你好", "assistant_response": "您好！我是您的智能客服助手，请问有什么可以帮助您的？"},
    {"user_query": "北京天气怎么样？", "assistant_response": "让我为您查询一下北京的实时天气信息。", "tool": "get_weather"},
    {"user_query": "你们有什么产品?", "assistant_response": "我们提供多种优质产品，包括电子产品、家居用品和数码配件。请问您对哪类产品感兴趣？"},
    {"user_query": "党的二十届四中全会说了什么？", "assistant_response": "让我从知识库中为您检索相关信息。", "tool": "retrieve_knowledge"},
    {"user_query": "我的订单什么时候发货?", "assistant_response": "为了帮您查询订单状态，请问可以提供一下您的订单号吗？"},
    {"user_query": "这个商品能退换吗?", "assistant_response": "我们支持7天无理由退换货服务。请问您是对哪款商品有疑问呢？"},
    {"user_query": "谢谢", "assistant_response": "不客气，很高兴能帮到您！如果还有其他问题，随时欢迎再来咨询。"}
]


def create_chat_prompt(system_prompt: str = CUSTOMER_SERVICE_PROMPT_TEMPLATE):
    """
    创建聊天提示模板（兼容 create_tool_calling_agent）

    参数:
        system_prompt: 系统提示文本

    返回:
        ChatPromptTemplate 实例
    """
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


def build_few_shot_system_prompt(
    examples: list = None,
    system_prompt: str = CUSTOMER_SERVICE_PROMPT_TEMPLATE,
    max_length: int = 2048
) -> str:
    """
    构建带有 FewShot 示例的系统提示文本

    LengthBasedExampleSelector 用于根据输入长度动态选择合适的示例，
    确保总提示长度不超过 max_length。

    参数:
        examples: 示例列表，格式: [{"user_query": "...", "assistant_response": "..."}, ...]
        system_prompt: 基础系统提示文本
        max_length: 最大提示长度，默认 2048

    返回:
        带有示例的系统提示文本字符串
    """
    if not examples:
        return system_prompt
    
    # 示例模板
    example_prompt = PromptTemplate(
        input_variables=["user_query", "assistant_response"],
        template="用户: {user_query}\n助手: {assistant_response}"
    )
    
    # 创建基于长度的示例选择器
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        example_prompt=example_prompt,
        max_length=max_length
    )
    
    # 获取选择的示例
    selected_examples = example_selector.select_examples({"input": ""})
    
    # 构建示例文本
    if selected_examples:
        examples_text = "\n\n".join([
            f"用户: {ex['user_query']}\n助手: {ex['assistant_response']}"
            for ex in selected_examples
        ])
        return f"{system_prompt}\n\n## 参考示例:\n{examples_text}"
    else:
        return system_prompt


def create_few_shot_prompt(
    examples: list = None,
    system_prompt: str = CUSTOMER_SERVICE_PROMPT_TEMPLATE,
    max_length: int = 2048
) -> ChatPromptTemplate:
    """
    创建带有 FewShot 示例的聊天提示模板（兼容 create_tool_calling_agent）

    参数:
        examples: 示例列表，格式: [{"user_query": "...", "assistant_response": "..."}, ...]
                  默认为 DEFAULT_FEW_SHOT_EXAMPLES，传 None 使用默认值，传 [] 禁用示例
        system_prompt: 基础系统提示文本
        max_length: 最大提示长度

    返回:
        ChatPromptTemplate 实例（与 create_chat_prompt 结构一致）
    """
    # 如果 examples 为 None，使用默认示例；如果为空列表，不使用示例
    # if examples is None:
    #     examples = DEFAULT_FEW_SHOT_EXAMPLES
    
    # 构建带有示例的系统提示文本
    few_shot_system_prompt = build_few_shot_system_prompt(
        examples=examples,
        system_prompt=system_prompt,
        max_length=max_length
    )
    
    # 使用 create_chat_prompt 创建结构一致的提示模板
    return create_chat_prompt(few_shot_system_prompt)


__all__ = [
    'create_few_shot_prompt',
]
