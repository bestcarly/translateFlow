import os
from dotenv import load_dotenv
import openai
import httpx
from .utils import retry_on_error
import logging

# 加载环境变量
load_dotenv()

def check_openai_environment():
    """
    检查OpenAI相关的环境变量配置
    Returns:
        tuple: (是否配置正确, 错误信息)
    """
    required_vars = {
        'OPENAI_API_KEY': '你的API密钥',
        'OPENAI_API_BASE': 'API基础URL',
        'OPENAI_MODEL': '使用的模型名称'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"- {var}: {description}")
    
    if missing_vars:
        error_message = "\n".join([
            "缺少必要的OpenAI配置，请按以下步骤设置：",
            "",
            "1. 确保项目根目录下存在 .env 文件",
            "2. 在 .env 文件中添加以下配置：",
            "",
            *missing_vars,
            "",
            "示例：",
            "OPENAI_API_KEY=sk-your-api-key",
            "OPENAI_API_BASE=https://your-api-base-url",
            "OPENAI_MODEL=your-model-name",
            "",
            "如果没有 .env 文件，可以复制 .env.example 作为模板：",
            "cp .env.example .env"
        ])
        return False, error_message
    
    return True, ""

# 检查环境变量
is_configured, error_message = check_openai_environment()
if not is_configured:
    print("\n⚠️ OpenAI配置错误")
    print("=" * 50)
    print(error_message)
    print("=" * 50)
    raise RuntimeError("OpenAI环境配置不完整")

# 配置OpenAI
API_KEY = os.getenv('OPENAI_API_KEY')
API_BASE = os.getenv('OPENAI_API_BASE')
DEFAULT_MODEL = os.getenv('OPENAI_MODEL')
PROXY = os.getenv('OPENAI_PROXY')

# 创建 httpx 客户端
try:
    if PROXY:
        # 修正代理设置格式
        proxies = {
            "http://": PROXY,
            "https://": PROXY
        }
        http_client = httpx.Client(
            proxies=proxies,
            verify=False
        )
    else:
        http_client = httpx.Client()
except Exception as e:
    print(f"Warning: Failed to create HTTP client: {e}")
    http_client = None

# 创建OpenAI客户端
try:
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=API_BASE,
        http_client=http_client,
    )
except Exception as e:
    print(f"Error: Failed to initialize OpenAI client: {e}")
    raise

@retry_on_error(
    max_retries=3,
    delay=2,
    backoff=2,
    exceptions=(
        openai.APIError,
        openai.APIConnectionError,
        openai.RateLimitError,
        openai.APITimeoutError,
    )
)
def qwen_chat(text_content_openai_chat, model_name=None):
    """
    使用通用API调用聊天模型
    Args:
        text_content_openai_chat: 输入文本
        model_name: 模型名称，如果不指定则使用环境变量中的默认模型
    Returns:
        翻译后的文本
    """
    try:
        completion = client.chat.completions.create(
            model=model_name or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text_content_openai_chat},
            ],
        )
        return completion.choices[0].message.content + "\n"
    except Exception as e:
        logging.error(f"OpenAI API 调用错误: {e}")
        raise  # 抛出异常以触发重试机制

# 保持 ollama_chat 作为别名以保持向后兼容
ollama_chat = qwen_chat
