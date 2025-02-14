# TranslateFlow

一个强大的 AI 驱动的文档翻译工具，支持批量将英文文本和Word文档翻译成中文。

## 特性

- 🚀 支持多种 AI 翻译服务 (OpenAI/Ollama)
- 📁 批量处理整个目录的文件
- 📄 支持 .txt 和 .docx 格式
- 🔄 自动分块处理长文本
- 📊 详细的翻译日志
- 🎯 标准化的输出命名
- 🔁 智能重试机制
  - 自动处理网络错误和服务临时故障
  - 指数退避重试策略
  - 详细的重试日志记录

## 安装

1. 确保已安装 Python 3.8 或更高版本
2. 克隆或下载本项目
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，配置必要的参数：
   ```text
   # OpenAI 服务配置
   OPENAI_API_KEY=你的API密钥
   OPENAI_API_BASE=API基础URL
   OPENAI_MODEL=使用的模型名称

   # Ollama 服务配置（如果使用 Ollama）
   OLLAMA_MODEL=qwen2.5:7b        # 使用的模型名称
   OLLAMA_API_BASE=http://localhost:11434/api  # 可选，默认为本地服务
   ```

## 使用方法

### 基本用法

1. 翻译单个文件：
   ```bash
   ./translate.sh path/to/file.txt     # Linux/Mac
   translate.bat path/to/file.txt      # Windows
   ```

2. 翻译整个目录：
   ```bash
   ./translate.sh path/to/directory    # Linux/Mac
   translate.bat path/to/directory     # Windows
   ```

3. 使用默认目录：
   ```bash
   ./translate.sh    # Linux/Mac
   translate.bat     # Windows
   ```
   将文件放在 `sourceFile` 目录中，翻译结果会保存在 `translateFile` 目录。

### 高级选项

- 设置分块大小：
  ```bash
  ./translate.sh --chunk_size 3000
  ```

- 选择翻译服务：
  ```bash
  ./translate.sh --service ollama  # 使用Ollama服务（使用.env中配置的模型）
  ./translate.sh --service openai  # 使用OpenAI服务（默认）
  ```

### 输出文件

- 翻译结果：`./translateFile/YYYYMMDD_HHMMSS_原文件名_译文.txt`
- 日志文件：`./logs/YYYYMMDD_HHMMSS/translate_YYYYMMDD_HHMMSS.log`

## 支持的文件格式

- 文本文件 (.txt)
- Word文档 (.docx)

## 注意事项

1. 确保网络连接稳定
2. 检查API密钥配置是否正确
3. 大文件会自动分块处理
4. 建议保持默认的分块大小(2000字符)以获得最佳翻译效果
5. 遇到临时错误时程序会自动重试
   - OpenAI服务：自动处理 API 错误、连接超时、限流等问题
   - Ollama服务：自动处理网络错误和服务异常
   - 最多重试3次，每次重试间隔时间递增
   - 重试过程可在日志文件中查看

> 注意：使用 Ollama 服务时，模型名称需要在 .env 文件中通过 OLLAMA_MODEL 参数配置 