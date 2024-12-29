# DoubaoTranslator: 基于豆包 API 的专业翻译工具包

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.2-green.svg)](https://pypi.org/project/doubaotrans/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)

[English](README.en.md) | 中文

DoubaoTranslator 是一个基于豆包 API 的专业翻译工具包，提供多语言翻译、术语表管理、上下文感知翻译和风格定制等功能。

## 功能特点

- **多语言支持**：支持 17 种主流语言之间的互译
- **上下文感知**：使用上下文窗口维持语义连贯性
- **术语管理**：自定义术语映射，确保专业准确性
- **风格模板**：预定义风格（正式、随意、技术、创意）
- **流式翻译**：实时翻译并返回部分结果
- **批量处理**：高效的批量翻译与并发控制
- **增强语言检测**：结合多个检测器的结果
- **性能优化**：缓存、重试机制、HTTP/2 支持
- **文档翻译**：支持长文档的上下文感知翻译
- **翻译评估**：提供翻译质量评估功能
- **异步支持**：完整的异步操作支持，包括上下文管理器

## 安装

```bash
pip install doubaotrans
```

## API 文档

### 初始化选项

```python
DoubaoTranslator(
    api_key: str = None,                    # API密钥（必选）
    model_name: str = None,                 # 模型名称（可选）
    base_url: str = None,                   # API基础URL（可选）
    max_workers: int = 5,                   # 最大并发数（可选）
    glossary_path: str = None,              # 术语表路径（可选）
    performance_mode: str = 'balanced',      # 性能模式（可选）：'fast', 'balanced', 'accurate'
    **kwargs                                # 其他性能参数（可选）
)
```

### 翻译方法

#### 基础翻译
```python
async def doubao_translate(
    text: Union[str, List[str]],           # 要翻译的文本或文本列表
    dest: str = 'en',                      # 目标语言（必选）
    src: str = 'auto',                     # 源语言（可选，默认自动检测）
    stream: bool = False                   # 是否使用流式翻译（可选）
) -> Union[DoubaoTranslated, List[DoubaoTranslated], AsyncGenerator]
```

#### 批量翻译
```python
async def translate_batch(
    texts: List[str],                      # 要翻译的文本列表
    dest: str = 'en',                      # 目标语言
    src: str = 'auto',                     # 源语言
    batch_size: int = 10                   # 批处理大小
) -> List[DoubaoTranslated]
```

#### 上下文感知翻译
```python
async def translate_with_context(
    text: str,                             # 要翻译的文本
    context: str,                          # 上下文信息
    dest: str = 'en',                      # 目标语言
    src: str = 'auto',                     # 源语言
    style_guide: str = None                # 风格指南
) -> DoubaoTranslated
```

#### 文档翻译
```python
async def translate_document_with_context(
    paragraphs: List[str],                 # 段落列表
    dest: str = 'en',                      # 目标语言
    src: str = 'auto',                     # 源语言
    context_window: int = 2,               # 上下文窗口大小
    batch_size: int = 5,                   # 批处理大小
    style_guide: str = None                # 风格指南
) -> List[DoubaoTranslated]
```

#### 风格化翻译
```python
async def translate_with_style(
    text: str,                             # 要翻译的文本
    dest: str = 'en',                      # 目标语言
    src: str = 'auto',                     # 源语言
    style: Union[str, Dict] = 'formal',    # 翻译风格
    context: str = None,                   # 上下文信息
    max_versions: int = 3                  # 最大版本数（创意风格）
) -> DoubaoTranslated
```

### 语言检测

#### 基础检测
```python
async def doubao_detect(
    text: str                              # 要检测的文本
) -> DoubaoDetected
```

#### 增强检测
```python
async def doubao_detect_enhanced(
    text: str                              # 要检测的文本
) -> DoubaoDetected
```

### 术语表管理

```python
def load_glossary(
    path: Union[str, Path]                 # 术语表文件路径
) -> None

def save_glossary(
    path: Union[str, Path]                 # 保存路径
) -> None

def add_term(
    term_id: str,                          # 术语ID
    translations: Dict[str, str]           # 各语言的翻译
) -> None

async def apply_glossary(
    text: str,                             # 要翻译的文本
    src: str,                              # 源语言
    dest: str                              # 目标语言
) -> DoubaoTranslated
```

### 翻译评估

```python
async def evaluate_translation(
    original: str,                         # 原文
    translated: str,                       # 译文
    src: str,                             # 源语言
    dest: str                             # 目标语言
) -> Dict[str, float]                     # 返回评分指标
```

### 性能配置

#### 预定义性能模式
```python
PERFORMANCE_PROFILES = {
    'fast': {
        'max_workers': 10,
        'cache_ttl': 1800,
        'min_request_interval': 0.05,
        'max_retries': 2,
        'timeout': 15,
        'temperature': 0.5,
        'max_tokens': 512,
    },
    'balanced': {
        'max_workers': 5,
        'cache_ttl': 3600,
        'min_request_interval': 0.1,
        'max_retries': 3,
        'timeout': 30,
        'temperature': 0.3,
        'max_tokens': 1024,
    },
    'accurate': {
        'max_workers': 3,
        'cache_ttl': 7200,
        'min_request_interval': 0.2,
        'max_retries': 5,
        'timeout': 60,
        'temperature': 0.1,
        'max_tokens': 2048,
    }
}
```

#### 自定义性能设置
```python
def set_performance_config(
    max_workers: int = None,               # 最大并发数
    cache_ttl: int = None,                 # 缓存有效期
    min_request_interval: float = None,     # 最小请求间隔
    max_retries: int = None,               # 最大重试次数
    timeout: int = None,                   # 超时时间
    temperature: float = None,             # 采样温度
    max_tokens: int = None                 # 最大标记数
) -> None
```

### 风格模板

```python
style_templates = {
    'formal': """
        翻译要求：
        1. 使用正式的学术用语
        2. 保持严谨的句式结构
        3. 使用标准的专业术语
        4. 避免口语化和简化表达
    """,
    'casual': """
        翻译要求：
        1. 使用日常口语表达
        2. 保持语言自然流畅
        3. 使用简短句式
        4. 可以使用常见缩写
    """,
    'technical': """
        翻译要求：
        1. 严格使用技术术语
        2. 保持专业准确性
        3. 使用规范的技术表达
        4. 保持术语一致性
    """,
    'creative': """
        翻译要求：
        1. 提供多个不同的翻译版本
        2. 每个版本使用不同的表达方式
        3. 保持原文的核心含义
        4. 限制在指定版本数以内
    """
}
```

### 工具方法

```python
async def test_connection() -> bool        # 测试API连接
def get_config() -> dict                   # 获取当前配置
def get_supported_languages() -> List[str]  # 获取支持的语言列表
def is_language_supported(
    lang_code: str                         # 语言代码
) -> bool                                  # 检查语言是否支持
```

### 异步上下文管理器支持

```python
async with DoubaoTranslator(api_key="your_api_key") as translator:
    result = await translator.doubao_translate("Hello", dest="zh")
```

### 返回对象

#### DoubaoTranslated
```python
class DoubaoTranslated:
    src: str          # 源语言代码
    dest: str         # 目标语言代码
    origin: str       # 原始文本
    text: str         # 翻译后的文本
    pronunciation: str # 发音（如果可用）
```

#### DoubaoDetected
```python
class DoubaoDetected:
    lang: str         # 检测到的语言代码
    confidence: float # 检测置信度（0.00 到 1.00）
    details: dict     # 额外的检测详情（用于增强检测）
```

### 异常类

```python
class DoubaoError(Exception)                    # 基础异常类
class DoubaoAuthenticationError(DoubaoError)    # 认证错误
class DoubaoConnectionError(DoubaoError)        # 连接错误
class DoubaoAPIError(DoubaoError)              # API调用错误
class DoubaoConfigError(DoubaoError)           # 配置错误
class DoubaoValidationError(DoubaoError)       # 输入验证错误
```

## 使用示例

### 基本翻译
```python
translator = DoubaoTranslator(api_key="your_api_key")

# 单个文本翻译
result = await translator.doubao_translate("Hello, World!", dest="zh")
print(result.text)  # 你好，世界！

# 批量翻译
texts = ["Hello", "World", "AI"]
results = await translator.translate_batch(texts, dest="zh")
for result in results:
    print(f"{result.origin} -> {result.text}")
```

### 上下文感知翻译
```python
# 文档翻译
paragraphs = [
    "这是第一段。关于人工智能的发展。",
    "这是第二段，继续讨论AI技术。",
    "最后一段总结AI的未来。"
]

results = await translator.translate_document_with_context(
    paragraphs=paragraphs,
    dest="en",
    context_window=2,
    style_guide="academic"
)

for result in results:
    print(result.text)
```

### 风格化翻译
```python
# 使用预定义风格
formal_result = await translator.translate_with_style(
    text="Hello",
    dest="zh",
    style="formal"
)

# 使用自定义风格
custom_style = {
    "语气": "正式",
    "表达方式": "简洁",
    "专业程度": "高"
}
custom_result = await translator.translate_with_style(
    text="Hello",
    dest="zh",
    style=custom_style
)
```

### 翻译评估
```python
scores = await translator.evaluate_translation(
    original="Hello, World!",
    translated="你好，世界！",
    src="en",
    dest="zh"
)
print(f"准确性: {scores['accuracy']}")
print(f"流畅性: {scores['fluency']}")
print(f"专业性: {scores['professionalism']}")
print(f"风格: {scores['style']}")
```

## 注意事项

1. API 限制
   - 每次请求的最大文本长度：5000 字符
   - 可能受 API 速率限制
   - 建议使用异步方法处理大量请求

2. 性能优化
   - 使用 HTTP/2 需要安装 `hyper` 包
   - 缓存机制可以减少重复请求
   - 批量处理可以提高效率

3. 错误处理
   - 所有异步方法都应使用 try-except 处理异常
   - 网络错误会自动重试
   - 认证错误需要检查 API 密钥

4. 最佳实践
   - 使用异步上下文管理器自动管理资源
   - 选择合适的性能模式
   - 合理设置上下文窗口大小
   - 定期保存术语表 