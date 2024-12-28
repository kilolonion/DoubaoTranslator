# DoubaoTranslator 文档

[简体中文](README.md) | [English](README_en.md)

## 目录
1. [简介](#简介)
2. [安装与配置](#安装与配置)
3. [核心功能](#核心功能)
4. [高级特性](#高级特性)
5. [性能配置](#性能配置)
6. [错误处理](#错误处理)
7. [API参考](#api参考)

## 简介

DoubaoTranslator 是一个基于豆包API的专业翻译工具包，提供多语言翻译、术语表支持、上下文感知和风格化翻译等功能。

### 核心特性
- **多语言支持**: 支持17种主流语言互译
- **智能翻译**: 上下文感知，保持语义连贯
- **术语管理**: 自定义术语表，确保专业准确性
- **风格定制**: 支持预定义和自定义翻译风格
- **异步处理**: 支持流式和批量异步翻译
- **性能优化**: 智能缓存、重试机制、并发控制

## 安装与配置

### 环境要求
```bash
# 必需依赖
pip install openai>=1.0.0
pip install httpx>=0.24.0
pip install tenacity>=8.0.0
pip install python-dotenv>=0.19.0
pip install aiohttp>=3.8.0
pip install langdetect>=1.0.9

# 可选依赖
pip install redis>=4.0.0  # 用于分布式缓存
```

### 环境变量配置
```bash
# 必需配置
ARK_API_KEY=your_api_key_here        # API密钥
ARK_BASE_URL=https://api.example.com # API基础URL
ARK_MODEL=model_name                 # 模型名称

# 可选配置
DOUBAO_CACHE_DIR=/path/to/cache      # 缓存目录
DOUBAO_LOG_LEVEL=INFO               # 日志级别：DEBUG/INFO/WARNING/ERROR
DOUBAO_MAX_RETRIES=3                # 最大重试次数
DOUBAO_TIMEOUT=30                   # 请求超时时间（秒）
```

### 初始化参数详解
```python
translator = DoubaoTranslator(
    # 基础配置
    api_key=None,              # API密钥，None时使用环境变量
    model_name=None,           # 模型名称，None时使用环境变量
    base_url=None,             # API基础URL，None时使用环境变量
    
    # 性能相关
    max_workers=5,             # 最大并发线程数
    performance_mode='balanced', # 性能模式：fast/balanced/accurate
    cache_ttl=3600,           # 缓存过期时间（秒）
    timeout=20,               # 请求超时时间（秒）
    
    # 功能相关
    glossary_path=None,        # 术语表路径，支持.json文件
    verify_ssl=True,          # 是否验证SSL证书
    proxies=None,             # 代理设置，如 {'http': 'http://proxy:port'}
    headers=None,             # 自定义请求头
    
    # 高级配置
    retry_times=3,            # 重试次数
    min_request_interval=0.1, # 最小请求间隔（秒）
    temperature=0.5,          # 创造性程度 (0.0-1.0)
    max_tokens=200,           # 最大令牌数
)
```

### 性能模式说明
1. 快速模式 (fast)
   - 适用场景：简单文本、实时翻译
   - 特点：响应快速，资源消耗低
   - 配置：较短的超时时间，较少的重试次数

2. 平衡模式 (balanced)
   - 适用场景：一般用途、日常翻译
   - 特点：平衡速度和质量
   - 配置：适中的超时时间和重试策略

3. 精确模式 (accurate)
   - 适用场景：专业文档、重要内容
   - 特点：注重准确性，资源消耗较高
   - 配置：较长的超时时间，更多的重试次数

### 缓存配置详解
```python
# 内存缓存配置
translator.configure_cache(
    cache_type='memory',      # 缓存类型：memory/redis
    max_size=1000,           # 最大缓存条目数
    ttl=3600                 # 过期时间（秒）
)

# Redis缓存配置
translator.configure_cache(
    cache_type='redis',
    cache_url='localhost:6379',
    ttl=3600,
    namespace='translation',  # 缓存命名空间
    password=None,           # Redis密码
    db=0                     # Redis数据库编号
)
```

## 核心功能

### 基本翻译
```python
# 单文本翻译
result = translator.doubao_translate(
    text="要翻译的文本",
    dest="en",                # 目标语言
    src="auto",               # 源语言（auto为自动检测）
    stream=False              # 是否使用流式传输
)

# 批量翻译
results = translator.doubao_translate(
    ["文本1", "文本2"],
    dest="en"
)
```

### 语言检测
```python
# 基础检测
detection = translator.doubao_detect("文本")
print(detection.lang)         # 检测到的语言
print(detection.confidence)   # 置信度

# 增强检测
detection = translator.doubao_detect_enhanced("混合语言文本")
print(detection.details)      # 详细语言分布信息
```

### 术语表功能
```python
# 加载术语表
translator.load_glossary("glossary.json")

# 更新术语
translator.add_term("AI", {
    "en": "Artificial Intelligence",
    "zh": "人工智能"
})

# 应用术语表翻译
result = translator.apply_glossary(
    text="包含术语的文本",
    src="zh",
    dest="en",
    strict_mode=True         # 严格模式
)
```

## 高级特性

### 上下文感知翻译
```python
# 基本上下文翻译
result = translator.translate_with_context(
    text="苹果发布新产品",
    context="��篇文章讨论了苹果公司的发展",
    dest="en",
    src="auto",
    style_guide=None  # 可选的风格指南
)

# 文档级翻译
paragraphs = [
    "第一段内容",
    "第二段内容",
    "第三段内容"
]
results = translator.translate_document_with_context(
    paragraphs=paragraphs,
    dest="en",
    src="auto",
    context_window=2,    # 上下文窗口大小
    batch_size=5         # 批处理大小
)
```

### 风格化翻译
```python
# 预定义风格
styles = {
    'formal': "正式学术风格",
    'casual': "日常口语风格",
    'technical': "技术文档风格",
    'creative': "创意作风格"
}

# 使用预定义风格
result = translator.translate_with_style(
    text="要翻译的文本",
    dest="en",
    style="formal",     # 使用预定义风格
    context=None        # 可选上下文
)

# 自定义风格
custom_style = {
    "语气": "幽默诙谐",
    "表达方式": "生动形象",
    "专业程度": "通俗易懂",
    "特殊要求": "可以适当添加比喻"
}
result = translator.translate_with_style(
    text="要翻译的文本",
    dest="en",
    style=custom_style  # 使用自定义风格
)
```

### 异步批量处理
```python
# 异步批量翻译
async def batch_translate():
    texts = ["文本1", "文本2", "文本3"]
    async with translator:
        results = await translator.translate_batch_async(
            texts=texts,
            dest="en",
            batch_size=5,
            progress_callback=lambda x, y: print(f"进度: {x}/{y}")
        )
    return results

# 运行异步翻译
import asyncio
results = asyncio.run(batch_translate())
```

## 性能配置

### 性能模式
```python
# 预定义的性能配置
PERFORMANCE_PROFILES = {
    'fast': {
        'max_retries': 2,
        'retry_min_wait': 0.5,
        'retry_max_wait': 2,
        'cache_ttl': 3600,
        'min_request_interval': 0.1,
        'max_tokens': 100,
        'temperature': 0.7,
        'timeout': 10,
        'max_workers': 5
    },
    'balanced': {
        'max_retries': 3,
        'retry_min_wait': 1,
        'retry_max_wait': 4,
        'cache_ttl': 7200,
        'min_request_interval': 0.2,
        'max_tokens': 200,
        'temperature': 0.5,
        'timeout': 20,
        'max_workers': 3
    },
    'accurate': {
        'max_retries': 5,
        'retry_min_wait': 2,
        'retry_max_wait': 8,
        'cache_ttl': 14400,
        'min_request_interval': 0.5,
        'max_tokens': 500,
        'temperature': 0.3,
        'timeout': 30,
        'max_workers': 2
    }
}
```

### 性能监控
```python
# 获取性能统计
stats = translator.metrics.get_statistics()
print(f"平均响应时间: {stats['average_response_time']}")
print(f"总请求数: {stats['total_requests']}")
print(f"错误率: {stats['error_rates']}")
print(f"平均请求大小: {stats['average_request_size']}")

# 评估翻译质量
scores = translator.evaluate_translation(
    original="原文",
    translated="译文",
    src="zh",
    dest="en"
)
print(f"准确性: {scores['accuracy']}")
print(f"流畅性: {scores['fluency']}")
print(f"专业性: {scores['professionalism']}")
print(f"风格: {scores['style']}")
```

## 错误处理

### 异常类型
```python
try:
    result = translator.doubao_translate("测试文本")
except DoubaoAuthenticationError as e:
    print("认证错误:", e)
except DoubaoConnectionError as e:
    print("连接错误:", e)
except DoubaoAPIError as e:
    print("API错误:", e)
```

### 重试机制
```python
# 配置重试策略
translator.configure_retry(
    max_retries=3,
    retry_conditions=[
        lambda e: isinstance(e, DoubaoConnectionError)
    ],
    retry_delay=1.0,
    backoff_factor=2.0
)

# 自定义重试回调
def retry_callback(retry_state):
    print(f"重试次数: {retry_state.attempt_number}")
translator.set_retry_callback(retry_callback)
```

## API参考

### 支持的语言
```python
DOUBAO_LANGUAGES = {
    'zh': 'chinese',    # 中文
    'en': 'english',    # 英语
    'ja': 'japanese',   # 日语
    'ko': 'korean',     # 韩语
    'fr': 'french',     # 法语
    'es': 'spanish',    # 西班牙语
    'ru': 'russian',    # 俄语
    'de': 'german',     # 德语
    'it': 'italian',    # 意大利语
    'tr': 'turkish',    # 土耳其语
    'pt': 'portuguese', # 葡萄牙语
    'vi': 'vietnamese', # 越南语
    'id': 'indonesian', # 印尼语
    'th': 'thai',       # 泰语
    'ms': 'malay',      # 马来语
    'ar': 'arabic',     # 阿拉伯语
    'hi': 'hindi'       # 印地语
}
```

### 工具方法
```python
# 测试连接
is_connected = translator.test_connection()

# 获取配置信息
config = translator.get_config()

# 验证语言支持
is_supported = translator.is_language_supported('en')

# 获取支持的语言列表
languages = translator.get_supported_languages()
```

### 缓存管理
```python
# 配置缓存
translator._cache_ttl = 3600           # 缓存过期时间（秒）
translator._min_request_interval = 0.1  # 最小请求间隔（秒）

# 清理缓存
translator._cleanup_cache()            # 清理过期缓存
```

## 使用限制

1. API限制
   - 单次请求最大文本长度：5000字符
   - 最大并发请求数：基于性能模式配置
   - 请求间隔：基于性能模式配置

2. 性能限制
   - 最大工作线程数：基于性能模式配置
   - 缓存条目数：基于可用内存
   - 批处理大小：推荐5-10条/批

3. 功能限制
   - 术语表最大条目数：无硬性限制，建议控制在合理范围
   - 上下文窗口大小：建议2-3段
   - 风格模板数量：预定义4种，支持自定义

## 高级应用场景

### 专业文档翻译
```python
# 科技文档翻译示例
result = translator.translate_with_context(
    text="量子计算在密码学领域的应用前景广阔",
    context="本文讨论了量子计算技术的最新发展",
    dest="en",
    style="technical"
)

# 医学文献翻译
medical_glossary = {
    "靶向治疗": {
        "en": "targeted therapy",
        "zh": "靶向治疗"
    },
    "免疫检查点": {
        "en": "immune checkpoint",
        "zh": "免疫检查点"
    }
}
translator.update_glossary(medical_glossary)
```

### 实时翻译系统
```python
async def real_time_translation_service():
    async def handle_message(websocket, path):
        async for message in websocket:
            # 语言检测
            detected = await translator.doubao_detect_enhanced(message)
            
            # 确定目标语言
            dest = 'en' if detected.lang == 'zh' else 'zh'
            
            # 流式翻译
            async for chunk in translator.doubao_translate_stream(
                text=message,
                dest=dest
            ):
                await websocket.send(chunk)

    server = await websockets.serve(
        handle_message, 
        'localhost', 
        8765
    )
    await server.wait_closed()
```

### 数据安全处理
```python
def sanitize_sensitive_data(text: str) -> str:
    """处理敏感信息"""
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{11}\b',
        'id_card': r'\b\d{17}[\dXx]\b'
    }
    
    for key, pattern in patterns.items():
        text = re.sub(pattern, f'[{key.upper()}]', text)
    return text

# 安全的翻译处理
text = "联系方式：john@example.com，电话：13812345678"
safe_text = sanitize_sensitive_data(text)
result = translator.doubao_translate(safe_text, dest='en')
```

### 性能优化实践
```python
# 批量翻译优化
async def optimized_batch_translation(texts: List[str], 
                                    batch_size: int = 5,
                                    max_concurrent: int = 3):
    semaphore = asyncio.Semaphore(max_concurrent)
    async with translator:
        tasks = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            task = asyncio.create_task(
                translate_with_semaphore(
                    batch, 
                    semaphore
                )
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

async def translate_with_semaphore(texts, semaphore):
    async with semaphore:
        return await translator.translate_batch_async(texts)
```


