import os
from dotenv import load_dotenv
import ollama
import logging
from .utils import retry_on_error

# 加载环境变量
load_dotenv()

# 获取Ollama配置
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')  # 如果未设置，使用默认值
API_BASE = os.getenv('OLLAMA_API_BASE')

# 如果设置了自定义API地址，配置Ollama客户端
if API_BASE:
    # 修改为新的API方式
    ollama.BASE_URL = API_BASE

@retry_on_error(
    max_retries=3,
    delay=2,
    backoff=2,
    exceptions=(Exception,)  # Ollama可能的异常类型
)
def ollama_chat(text_content_ollama_chat, model_name=None):
    """
    使用Ollama服务进行文本翻译
    Args:
        text_content_ollama_chat: 待翻译的文本内容
        model_name: 可选，指定使用的模型名称，如果不指定则使用环境变量中的配置
    Returns:
        翻译后的文本
    """
    try:
        # 使用指定的模型名称，如果未指定则使用环境变量中的配置
        model = model_name or DEFAULT_MODEL
        
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": text_content_ollama_chat,
                },
            ],
        )
        return response["message"]["content"]
    except Exception as e:
        logging.error(f"Ollama API 调用错误: {e}")
        raise  # 抛出异常以触发重试机制
