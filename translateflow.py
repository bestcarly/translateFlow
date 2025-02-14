import os
from dotenv import load_dotenv
import argparse
import logging
from docx import Document
from llm_model import openai_model
from tqdm import tqdm
from datetime import datetime

# 确保环境变量被加载
load_dotenv()

# 获取程序启动时间
START_TIME = datetime.now()
TIME_STR = START_TIME.strftime("%Y%m%d_%H%M%S")

# 创建日志目录
LOG_DIR = os.path.join("logs", TIME_STR)
os.makedirs(LOG_DIR, exist_ok=True)

# 创建翻译文件输出目录
TRANSLATE_DIR = "translateFile"
os.makedirs(TRANSLATE_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    filename=os.path.join(LOG_DIR, f"translate_{TIME_STR}.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def check_environment():
    required_vars = ['OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_MODEL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return False
    return True

def generate_output_filename(input_filename):
    """生成标准化的输出文件名"""
    base_name = os.path.splitext(input_filename)[0]
    return f"{TIME_STR}_{base_name}_译文.txt"

def translate_text(text, service="openai"):
    """
    使用AI模型进行文本翻译
    Args:
        text: 待翻译的文本
        service: 使用的服务类型，可选 'openai' 或 'ollama'
    """
    # 构造翻译提示文本
    text_content = f"""
    <任务> 您是一名精通简体中文的专业译者，你在文稿翻译方面有着非凡的能力。请协助我把英文内容翻译成简体中文。
    <注意>
    请根据英文内容进行翻译，维持原有的格式，不省略任何信息。你只负责返回翻译，不要回答或解释任何情况。
    对下面要翻译的内容进行翻译
    <翻译内容>
    {text}
    """
    
    if service.lower() == "ollama":
        from llm_model import ollama_model
        return ollama_model.ollama_chat(text_content)
    else:
        from llm_model import openai_model
        return openai_model.qwen_chat(text_content)


def split_text_by_line(text, max_chunk_size=4096):
    # 按行分割文本
    lines = text.splitlines()
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) <= max_chunk_size:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def extract_text_from_file(file_path):
    """
    从文件中提取文本内容，支持txt和docx格式
    """
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(
            [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
        )
    else:
        raise ValueError(
            "Unsupported file format. Only .txt and .docx files are supported."
        )


def translate_file(file_path, max_chunk_size=2000, service="openai"):
    text = extract_text_from_file(file_path)
    chunks = split_text_by_line(text, max_chunk_size)
    translated_chunks = []

    for chunk in tqdm(chunks, desc=f"Translating {os.path.basename(file_path)}", ncols=100):
        translated_chunk = translate_text(chunk, service)
        translated_chunks.append(translated_chunk)

        logging.info("-------------本批次翻译原文开始-------------------")
        logging.info(f"{chunk}")
        logging.info("-------------本批次翻译原文结束-------------------")
        logging.info("-------------本批次翻译译文开始-------------------")
        logging.info(f"{translated_chunk}")
        logging.info("-------------本批次翻译译文结束-------------------")

    return "".join(translated_chunks)


def process_directory(directory, max_chunk_size=2000, output_dir=None, service="openai"):
    """
    处理目录或单个文件的翻译
    Args:
        directory: 输入的目录或文件路径
        max_chunk_size: 最大分块大小
        output_dir: 输出目录，如果为None则使用默认的translateFile目录
        service: 使用的翻译服务，可选 'openai' 或 'ollama'
    """
    if os.path.isfile(directory):
        files_to_process = [os.path.basename(directory)]
        base_dir = os.path.dirname(directory)
    else:
        files_to_process = [
            f for f in os.listdir(directory)
            if f.endswith((".txt", ".docx")) and not f.startswith(TIME_STR)
        ]
        base_dir = directory

    # 使用默认的translateFile目录如果没有指定输出目录
    output_dir = output_dir or TRANSLATE_DIR

    for filename in tqdm(files_to_process, desc="Processing files", ncols=100):
        file_path = os.path.join(base_dir, filename)
        translated_text = translate_file(file_path, max_chunk_size, service)

        new_filename = generate_output_filename(filename)
        new_file_path = os.path.join(output_dir, new_filename)

        with open(new_file_path, "w", encoding="utf-8") as new_file:
            new_file.write(translated_text)


def main():
    if not check_environment():
        return

    parser = argparse.ArgumentParser(
        description="""
文本翻译工具 (Text Translation Tool)
-----------------------------------
这个工具可以将英文文本文件或Word文档翻译成中文。支持批量处理目录中的文件。

特性:
- 支持 .txt 和 .docx 格式文件
- 支持单个文件或整个目录的处理
- 可选择使用 OpenAI 或 Ollama 翻译服务
- 自动分块处理长文本
- 生成详细的翻译日志
- 标准化的输出文件命名

输出位置:
- 翻译文件: ./translateFile/YYYYMMDD_HHMMSS_原文件名_译文.txt
- 日志文件: ./logs/YYYYMMDD_HHMMSS/translate_YYYYMMDD_HHMMSS.log
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path", 
        nargs="?",
        type=str, 
        help="""
要翻译的文件或目录的路径。
- 如果指定文件路径：直接翻译该文件
- 如果指定目录路径：翻译该目录下所有支持的文件
- 如果不指定路径：使用默认的 sourceFile 目录
        """
    )
    
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=2000,
        help="""
单次翻译的最大字符数 (默认: 2000)。
较大的值可能加快翻译速度，但可能降低翻译质量或触发API限制。
建议范围: 1000-4000
        """
    )
    
    parser.add_argument(
        "--service",
        type=str,
        choices=["openai", "ollama"],
        default="openai",
        help="""
选择要使用的翻译服务:
- openai: 使用 OpenAI API (默认)
- ollama: 使用本地 Ollama 服务
确保在 .env 文件中正确配置了相应的服务参数。
        """
    )

    args = parser.parse_args()
    
    if args.path:
        process_directory(args.path, args.chunk_size, service=args.service)
    else:
        source_dir = "sourceFile"
        
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
            print(f"Created source directory: {source_dir}")
            print("Please put your files in the sourceFile directory and run again.")
            return
            
        process_directory(source_dir, args.chunk_size, service=args.service)


if __name__ == "__main__":
    main()
