# DoubaoTranslator Documentation

[简体中文](README.md) | [English](README_en.md)

## Table of Contents
1. [Introduction](#introduction)
2. [Installation & Configuration](#installation--configuration)
3. [Core Features](#core-features)
4. [Advanced Features](#advanced-features)
5. [Performance Configuration](#performance-configuration)
6. [Error Handling](#error-handling)
7. [API Reference](#api-reference)

## Introduction

DoubaoTranslator is a professional translation toolkit built on the Doubao API, offering multilingual translation, glossary support, context-aware translation, and style customization features.

### Core Features
- **Multilingual Support**: Translation between 17 mainstream languages
- **Intelligent Translation**: Context-aware with semantic coherence
- **Terminology Management**: Custom glossary for professional accuracy
- **Style Customization**: Predefined and custom translation styles
- **Async Processing**: Stream and batch async translation
- **Performance Optimization**: Smart caching, retry mechanisms, concurrency control

## Installation & Configuration

### Requirements
```bash
# Required dependencies
pip install openai>=1.0.0
pip install httpx>=0.24.0
pip install tenacity>=8.0.0
pip install python-dotenv>=0.19.0
pip install aiohttp>=3.8.0
pip install langdetect>=1.0.9

# Optional dependencies
pip install redis>=4.0.0  # For distributed caching
```

### Environment Configuration
```bash
# .env file
ARK_API_KEY=your_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=ep-20241114093010-dm56w
```

### Initialization Options
```python
translator = DoubaoTranslator(
    api_key=None,              # API key, env var takes precedence
    model_name=None,           # Model name, defaults to env var
    base_url=None,             # API base URL
    max_workers=5,             # Maximum concurrent threads
    glossary_path=None,        # Glossary file path
    performance_mode='balanced' # Mode: fast/balanced/accurate
)
```

## Core Features

### Basic Translation
```python
# Single text translation
result = translator.doubao_translate(
    text="The latest research in artificial intelligence",
    dest="zh",                # Target language
    src="auto",               # Source language (auto for detection)
    stream=False              # Stream mode
)

# Batch translation
results = translator.doubao_translate(
    ["Hello world", "Machine learning is fascinating"],
    dest="zh"
)
```

### Language Detection
```python
# Basic detection
detection = translator.doubao_detect("Hello, this is a test")
print(detection.lang)         # Detected language
print(detection.confidence)   # Confidence score

# Enhanced detection
detection = translator.doubao_detect_enhanced("Hello 你好")
print(detection.details)      # Detailed language distribution
```

### Glossary Management
```python
# Load glossary
translator.load_glossary("tech_glossary.json")

# Update terms
translator.add_term("ML", {
        "en": "Machine Learning",
        "zh": "机器学习",
        "ja": "機械学習"
})

# Apply glossary translation
result = translator.apply_glossary(
    text="ML and AI are transforming industries",
    src="en",
    dest="zh",
    strict_mode=True         # Strict mode
)
```

## Advanced Features

### Context-Aware Translation
```python
# Basic context translation
result = translator.translate_with_context(
    text="Apple unveiled groundbreaking products",
    context="This article discusses Apple Inc.'s technological innovations",
    dest="zh",
    src="auto",
    style_guide=None  # Optional style guide
)

# Document-level translation
paragraphs = [
    "The tech industry is evolving rapidly.",
    "AI systems are becoming increasingly sophisticated.",
    "Companies are adapting to these changes."
]
results = translator.translate_document_with_context(
    paragraphs=paragraphs,
    dest="zh",
    src="auto",
    context_window=2,    # Context window size
    batch_size=5         # Batch size
)
```

### Style Customization
```python
# Predefined styles
styles = {
    'formal': "Academic and professional tone",
    'casual': "Conversational and friendly tone",
    'technical': "Technical documentation style",
    'creative': "Creative writing style"
}

# Using predefined style
result = translator.translate_with_style(
    text="AI is revolutionizing healthcare",
    dest="zh",
    style="technical",   # Use predefined style
    context=None         # Optional context
)

# Custom style
custom_style = {
    "tone": "professional",
    "expression": "concise",
    "technical_level": "expert",
    "special_requirements": "maintain industry terminology"
}
result = translator.translate_with_style(
    text="Recent advances in quantum computing",
    dest="zh",
    style=custom_style  # Use custom style
)
```

### Async Batch Processing
```python
# Async batch translation
async def batch_translate():
    texts = [
        "Sustainable energy solutions",
        "Digital transformation trends",
        "Cloud computing innovations"
    ]
    async with translator:
        results = await translator.translate_batch_async(
            texts=texts,
            dest="zh",
            batch_size=5,
            progress_callback=lambda x, y: print(f"Progress: {x}/{y}")
        )
    return results

# Run async translation
import asyncio
results = asyncio.run(batch_translate())
```

## Advanced Use Cases

### Professional Document Translation
```python
# Scientific Paper Translation
result = translator.translate_with_context(
    text="Recent advances in quantum computing have shown promising applications in cryptography",
    context="This paper discusses the latest developments in quantum computing technology",
    dest="zh",
    style="technical"
)

# Medical Literature Translation
medical_glossary = {
    "immunotherapy": {
        "en": "immunotherapy",
        "zh": "免疫疗法",
        "ja": "免疫療法"
    },
    "biomarker": {
        "en": "biomarker",
        "zh": "生物标志物",
        "ja": "バイオマーカー"
    }
}
translator.update_glossary(medical_glossary)
```

### Real-Time Translation System
```python
async def real_time_translation_service():
    async def handle_message(websocket, path):
        async for message in websocket:
            # Language detection
            detected = await translator.doubao_detect_enhanced(message)
            
            # Determine target language
            dest = 'zh' if detected.lang == 'en' else 'en'
            
            # Stream translation
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

### Data Security Handling
```python
def sanitize_sensitive_data(text: str) -> str:
    """Handle sensitive information"""
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    }
    
    for key, pattern in patterns.items():
        text = re.sub(pattern, f'[{key.upper()}]', text)
    return text

# Secure translation processing
text = "Contact: john.doe@example.com, SSN: 123-45-6789"
safe_text = sanitize_sensitive_data(text)
result = translator.doubao_translate(safe_text, dest='zh')
```

### Performance Optimization
```python
# Optimized batch translation
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

### Enterprise Integration Examples
```python
# API Gateway Integration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = 'auto'
    target_lang: str = 'zh'
    style: Optional[str] = None

@app.post("/translate")
async def translate_endpoint(request: TranslationRequest):
    try:
        result = await translator.translate_with_style(
            text=request.text,
            src=request.source_lang,
            dest=request.target_lang,
            style=request.style
        )
        return {"translation": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Performance Configuration

### Performance Modes
```python
# Predefined performance profiles
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

### Performance Monitoring
```python
# Get performance statistics
stats = translator.metrics.get_statistics()
print(f"Average response time: {stats['average_response_time']}")
print(f"Total requests: {stats['total_requests']}")
print(f"Error rates: {stats['error_rates']}")
print(f"Average request size: {stats['average_request_size']}")

# Evaluate translation quality
scores = translator.evaluate_translation(
    original="Quantum computing is transforming cryptography",
    translated="量子计算正在改变密码学",
    src="en",
    dest="zh"
)
print(f"Accuracy: {scores['accuracy']}")
print(f"Fluency: {scores['fluency']}")
print(f"Technical accuracy: {scores['professionalism']}")
print(f"Style consistency: {scores['style']}")
```

## Error Handling

### Exception Types
```python
try:
    result = translator.doubao_translate("Test translation")
except DoubaoAuthenticationError as e:
    print("Authentication error:", e)
except DoubaoConnectionError as e:
    print("Connection error:", e)
except DoubaoAPIError as e:
    print("API error:", e)
```

### Retry Mechanism
```python
# Configure retry strategy
translator.configure_retry(
    max_retries=3,
    retry_conditions=[
        lambda e: isinstance(e, DoubaoConnectionError)
    ],
    retry_delay=1.0,
    backoff_factor=2.0
)

# Custom retry callback
def retry_callback(retry_state):
    print(f"Retry attempt: {retry_state.attempt_number}")
translator.set_retry_callback(retry_callback)
```

## API Reference

### Supported Languages
```python
DOUBAO_LANGUAGES = {
    'zh': 'chinese',    # Chinese
    'en': 'english',    # English
    'ja': 'japanese',   # Japanese
    'ko': 'korean',     # Korean
    'fr': 'french',     # French
    'es': 'spanish',    # Spanish
    'ru': 'russian',    # Russian
    'de': 'german',     # German
    'it': 'italian',    # Italian
    'tr': 'turkish',    # Turkish
    'pt': 'portuguese', # Portuguese
    'vi': 'vietnamese', # Vietnamese
    'id': 'indonesian', # Indonesian
    'th': 'thai',       # Thai
    'ms': 'malay',      # Malay
    'ar': 'arabic',     # Arabic
    'hi': 'hindi'       # Hindi
}
```

### Utility Methods
```python
# Test connection
is_connected = translator.test_connection()

# Get configuration
config = translator.get_config()

# Verify language support
is_supported = translator.is_language_supported('en')

# Get supported languages
languages = translator.get_supported_languages()
```

### Cache Management
```python
# Configure cache
translator._cache_ttl = 3600           # Cache TTL (seconds)
translator._min_request_interval = 0.1  # Min request interval (seconds)

# Clean cache
translator._cleanup_cache()            # Clear expired cache entries
```

## Usage Limitations

1. API Limitations
   - Maximum text length per request: 5000 characters
   - Maximum concurrent requests: Based on performance mode
   - Request interval: Based on performance mode

2. Performance Limitations
   - Maximum worker threads: Based on performance mode
   - Cache entries: Based on available memory
   - Batch size: Recommended 5-10 items/batch

3. Feature Limitations
   - Glossary entries: No hard limit, recommend reasonable size
   - Context window size: Recommended 2-3 paragraphs
   - Style templates: 4 predefined, custom styles supported 
