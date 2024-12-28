# DoubaoTranslator Documentation

[简体中文](doubaotrans.md) | [English](doubaotrans_en.md)

## Table of Contents
1. [Introduction](#introduction)
2. [Installation & Configuration](#installation--configuration)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Performance Tuning](#performance-tuning)
6. [Error Handling](#error-handling)
7. [API Reference](#api-reference)
8. [Best Practices](#best-practices)
9. [FAQ](#faq)
10. [Performance Benchmarks](#performance-benchmarks)
11. [Version History](#version-history)
12. [Limitations & Constraints](#limitations--constraints)
13. [Troubleshooting Guide](#troubleshooting-guide)
14. [Advanced Troubleshooting](#advanced-troubleshooting)

## Introduction

DoubaoTranslator is a professional translation toolkit built on the Doubao API. It provides comprehensive translation capabilities including basic translation, batch processing, language detection, glossary management, context-aware translation, and style customization.

### Core Features
- **Multilingual Support**: Translation between 20+ mainstream languages
- **Intelligent Translation**: Context-aware with semantic coherence
- **Professional Terminology**: Custom glossary support for domain-specific accuracy
- **Style Customization**: Multiple predefined and custom styles
- **High Performance**: Async processing, smart caching, batch translation
- **Reliability**: Comprehensive error handling and retry mechanisms
- **Extensibility**: Modular design for feature extensions
- **Async Processing**: Support for async batch translation
- **Streaming**: Support for large text streaming
- **Performance Monitoring**: Built-in metrics tracking

### Use Cases
- Document Localization
- API Response Translation
- Real-time Chat Translation
- Technical Documentation
- Multilingual Website Content
- Subtitle Translation 

## Installation & Configuration

### System Requirements
- Python 3.7+
- Memory: 4GB+ recommended
- Disk Space: 100MB minimum
- Network: Stable internet connection

### Dependencies
```bash
pip install openai>=1.0.0
pip install httpx>=0.24.0
pip install tenacity>=8.0.0
pip install python-dotenv>=0.19.0
pip install aiohttp>=3.8.0
pip install cachetools>=5.0.0
pip install langdetect>=1.0.9
pip install redis>=4.0.0
pip install pytest>=7.0.0
```

### Installation Steps
1. Using pip (recommended):
```bash
pip install doubaotrans
```

2. From source:
```bash
git clone https://github.com/yourusername/doubaotrans.git
cd doubaotrans
pip install -e .
``` 

## Basic Usage

### Initialization
```python
translator = DoubaoTranslator(
    api_key="your_api_key",              # API key
    model_name="model_name",             # Model name
    base_url="https://api.example.com",  # API base URL
    max_workers=5,                       # Maximum worker threads
    glossary_path="glossary.json",       # Glossary path
    performance_mode="balanced",         # Performance mode
    cache_ttl=3600,                     # Cache TTL
    timeout=20                          # Request timeout
)
```

### Basic Translation
1. Simple text translation:
```python
# Basic usage
result = translator.doubao_translate("Hello, world!", dest='zh')
print(result.text)  # 你好，世界！

# Specify source language
result = translator.doubao_translate(
    text="Hello, world!",
    src='en',
    dest='zh'
)
print(result.text)

# Formatted text
result = translator.doubao_translate(
    text="**Hello** _world_!",
    dest='zh',
    preserve_formatting=True  # Preserve markdown formatting
)
```

### Language Detection
```python
# Basic detection
detection = translator.doubao_detect("This is English text")
print(f"Language: {detection.lang}, Confidence: {detection.confidence}")

# Enhanced detection
detection = translator.doubao_detect_enhanced("Mixed language 混合语言")
print(detection.details)  # Contains detailed language distribution
```

### Batch Translation
```python
# Simple batch
texts = ["Hello", "World", "AI"]
results = translator.doubao_translate(texts, dest='zh')

# With progress callback
def progress_callback(completed, total):
    print(f"Progress: {completed}/{total}")

results = translator.doubao_translate(
    texts=texts,
    dest='zh',
    batch_size=5,
    progress_callback=progress_callback
)
``` 

## Advanced Features

### Streaming Translation
```python
# Basic streaming
result = translator.doubao_translate(
    text="This is a very long text...",
    dest='zh',
    stream=True
)

# Streaming with callback
def stream_callback(chunk):
    print(f"Received chunk: {chunk}")

result = translator.doubao_translate(
    text="Long text...",
    dest='zh',
    stream=True,
    chunk_callback=stream_callback
)
```

### Glossary Management
1. Creating glossary:
```python
glossary_data = {
    "AI": {
        "en": "Artificial Intelligence",
        "zh": "人工智能",
        "ja": "人工知能"
    },
    "ML": {
        "en": "Machine Learning",
        "zh": "机器学习",
        "ja": "機械学習"
    }
}

# Save glossary
translator.save_glossary(glossary_data, "my_glossary.json")

# Load glossary
translator.load_glossary("my_glossary.json")

# Dynamic update
translator.update_glossary({
    "NLP": {
        "en": "Natural Language Processing",
        "zh": "自然语言处理"
    }
})
```

2. Using glossary:
```python
# Apply glossary translation
result = translator.apply_glossary(
    text="AI and ML in NLP field",
    src='en',
    dest='zh',
    strict_mode=True  # Ensure all terms are replaced
)

# Term extraction
terms = translator.extract_terms(
    text="This article discusses AI and ML technology",
    return_positions=True  # Return term positions in text
)
```

### Performance Monitoring
```python
# Get performance statistics
stats = translator.metrics.get_statistics()
print(f"Average response time: {stats['average_response_time']}")
print(f"Total requests: {stats['total_requests']}")
print(f"Error rates: {stats['error_rates']}")

# Generate performance report
report = translator.generate_performance_report(
    include_details=True,
    format='markdown'
)
```

### Async Batch Processing
```python
async def translate_batch():
    texts = ["Text1", "Text2", "Text3"]
    async with translator:
        results = await translator.translate_batch_async(
            texts=texts,
            dest='zh',
            batch_size=2,
            progress_callback=lambda x, y: print(f"Progress: {x}/{y}")
        )
    return results

# Run async batch translation
import asyncio
results = asyncio.run(translate_batch())
``` 

## Performance Tuning

### Performance Modes
```python
# Fast mode
fast_translator = DoubaoTranslator(
    performance_mode='fast',
    max_workers=8
)

# Balanced mode
balanced_translator = DoubaoTranslator(
    performance_mode='balanced',
    max_workers=4
)

# Accurate mode
accurate_translator = DoubaoTranslator(
    performance_mode='accurate',
    max_workers=2
)
```

### Custom Performance Configuration
```python
# Detailed performance configuration
translator.set_performance_config(
    max_tokens=300,          # Maximum tokens
    temperature=0.4,         # Creativity level
    timeout=20,              # Request timeout
    cache_ttl=3600,         # Cache TTL
    max_workers=4,          # Maximum workers
    min_request_interval=0.1,# Request interval
    retry_multiplier=1.5,    # Retry interval multiplier
    max_retries=3,          # Maximum retries
    batch_size=5            # Batch size
)
```

### Cache Configuration
```python
# Configure cache
translator.configure_cache(
    cache_type='redis',          # Cache type
    cache_url='localhost:6379',  # Cache server
    ttl=3600,                   # Expiration time
    max_size=1000               # Maximum entries
)

# Clear cache
translator.clear_cache()
translator.clear_expired_cache()
```

## Error Handling

### Error Types
```python
try:
    result = translator.doubao_translate("test text")
except DoubaoAuthenticationError as e:
    print("Authentication error:", e)
except DoubaoConnectionError as e:
    print("Connection error:", e)
except DoubaoAPIError as e:
    print("API error:", e)
except DoubaoRateLimitError as e:
    print("Rate limit:", e)
except DoubaoTimeoutError as e:
    print("Timeout error:", e)
except DoubaoValidationError as e:
    print("Validation error:", e)
```

### Retry Mechanism
```python
# Configure retry strategy
translator.configure_retry(
    max_retries=3,
    retry_conditions=[
        lambda e: isinstance(e, DoubaoConnectionError),
        lambda e: isinstance(e, DoubaoTimeoutError)
    ],
    retry_delay=1.0,
    backoff_factor=2.0
)

# Custom retry callback
def retry_callback(retry_state):
    print(f"Retrying... Attempt {retry_state.attempt_number}")

translator.set_retry_callback(retry_callback)
```

## Troubleshooting Guide

1. API Authentication Failures
   - Check if API key is correct
   - Verify API key expiration
   - Confirm API permissions
   - Check environment variables

2. Connection Timeouts
   - Check network stability
   - Verify firewall settings
   - Try increasing timeout settings
   - Consider using a proxy

3. Rate Limit Errors
   - Check current API usage
   - Implement request throttling
   - Consider upgrading API plan
   - Use caching to reduce requests

4. Translation Quality Issues
   - Ensure correct source text formatting
   - Try using more context
   - Check and update glossary
   - Consider domain-specific models

5. Performance Issues
   - Use async batch processing
   - Optimize cache strategy
   - Adjust performance parameters
   - Monitor performance metrics

6. Memory Issues
   - Use streaming for large documents
   - Optimize memory usage
   - Increase system memory
   - Process data in batches

7. Language Detection Issues
   - Provide sufficient text samples
   - Use enhanced detection method
   - Manually specify source language
   - Update to latest version

8. Concurrency Issues
   - Check max_workers setting
   - Use asyncio for async operations
   - Implement proper thread pool management
   - Monitor thread usage

## Advanced Troubleshooting

1. Log Analysis
   - Enable detailed logging
   - Use log analysis tools
   - Create custom log filters

2. Network Diagnostics
   - Monitor API calls
   - Check latency and packet loss
   - Consider using CDN

3. Load Testing
   - Conduct comprehensive load tests
   - Simulate various usage patterns
   - Optimize based on results

4. Security Audit
   - Regular vulnerability scanning
   - Ensure HTTPS usage
   - Implement access controls

5. Data Consistency
   - Implement integrity checks
   - Verify cache consistency
   - Establish backup strategy

6. Automated Monitoring
   - Set up monitoring systems
   - Configure alert thresholds
   - Implement auto-recovery

7. Code Review
   - Regular code reviews
   - Use performance profiling
   - Consider refactoring

8. User Feedback
   - Establish feedback collection
   - Analyze problem patterns
   - Prioritize common issues

## Version History

### v1.0.0 (2024-12-20)
- Initial release
- Basic translation features
- Glossary support
- Context-aware translation

### v1.1.0 (2024-12-25)
- Added style customization
- Improved performance config
- Enhanced error handling
- Added async support

### v1.2.0 (2024-12-28)
- Added streaming translation
- Improved caching
- Added performance monitoring
- Custom retry support 

## API Reference

### Main Classes

#### DoubaoTranslator
```python
class DoubaoTranslator:
    """Main translator class"""
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        max_workers: int = 5,
        glossary_path: Optional[str] = None,
        performance_mode: str = 'balanced',
        **kwargs
    ):
        """
        Initialize translator
        
        Args:
            api_key: API key
            model_name: Model name
            base_url: API base URL
            max_workers: Maximum worker threads
            glossary_path: Glossary path
            performance_mode: Performance mode
            **kwargs: Additional configuration
        """
        pass

    def doubao_translate(
        self,
        text: Union[str, List[str]],
        dest: str = 'en',
        src: str = 'auto',
        stream: bool = False,
        **kwargs
    ) -> Union[DoubaoTranslated, List[DoubaoTranslated]]:
        """
        Translate text
        
        Args:
            text: Text or list of texts to translate
            dest: Target language
            src: Source language
            stream: Whether to use streaming
            **kwargs: Additional parameters
            
        Returns:
            Translation result object or list of results
        """
        pass

#### DoubaoTranslated
```python
class DoubaoTranslated:
    """Translation result class"""
    def __init__(
        self,
        src: str,
        dest: str,
        origin: str,
        text: str,
        pronunciation: Optional[str] = None
    ):
        """
        Initialize translation result
        
        Args:
            src: Source language
            dest: Target language
            origin: Original text
            text: Translated text
            pronunciation: Pronunciation (optional)
        """
        pass
```

### Constants

```python
# Supported language codes
DOUBAO_LANGUAGES = {
    'zh': 'chinese',
    'en': 'english',
    'ja': 'japanese',
    'ko': 'korean',
    'fr': 'french',
    'de': 'german',
    'es': 'spanish',
    'it': 'italian',
    'ru': 'russian',
    'pt': 'portuguese',
    'ar': 'arabic',
    'hi': 'hindi',
    'th': 'thai',
    'vi': 'vietnamese'
}

# Performance mode configurations
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

## Limitations & Constraints

### API Limitations
- Maximum text length per request: 5000 characters
- Maximum requests per second: 20
- Daily request quota: Based on plan

### Performance Limitations
- Maximum concurrent connections: 20
- Maximum batch size: 100 items
- Maximum cache entries: 10000

### Feature Limitations
- Maximum document size: 10MB
- Maximum glossary entries: 1000
- Maximum context length: 2000 characters

## Best Practices

### Performance Optimization
1. Choose appropriate performance mode:
   - Fast mode: Simple texts, real-time translation
   - Balanced mode: General usage
   - Accurate mode: Professional documents

2. Batch processing:
   - Use appropriate batch size (5-10 recommended)
   - Enable async processing
   - Implement progress callbacks

3. Cache strategy:
   - Enable caching for frequently translated content
   - Clean expired cache regularly
   - Use distributed caching for better performance

4. Resource management:
   - Control concurrent requests
   - Implement request throttling
   - Release resources promptly 

## Security Best Practices

### API Key Management
1. Environment Variables
   ```python
   # Use environment variables for sensitive data
   from dotenv import load_dotenv
   load_dotenv()
   
   translator = DoubaoTranslator(
       api_key=os.getenv('ARK_API_KEY')
   )
   ```

2. Key Rotation
   - Regularly rotate API keys
   - Use temporary keys for testing
   - Monitor key usage patterns

3. Access Control
   - Implement role-based access
   - Limit API key permissions
   - Log all key usage

### Data Security
1. Data Encryption
   ```python
   # Enable HTTPS
   translator = DoubaoTranslator(
       base_url="https://api.example.com",
       verify_ssl=True
   )
   ```

2. Data Sanitization
   ```python
   # Sanitize sensitive information
   def sanitize_text(text: str) -> str:
       # Remove sensitive patterns
       text = re.sub(r'\b\d{16}\b', '[CREDIT_CARD]', text)
       text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
       return text

   result = translator.doubao_translate(sanitize_text(text))
   ```

## Advanced Usage Examples

### Custom Translation Pipeline
```python
class TranslationPipeline:
    def __init__(self, translator: DoubaoTranslator):
        self.translator = translator
        self.preprocessors = []
        self.postprocessors = []
    
    def add_preprocessor(self, func):
        self.preprocessors.append(func)
    
    def add_postprocessor(self, func):
        self.postprocessors.append(func)
    
    def translate(self, text: str) -> str:
        # Apply preprocessors
        for proc in self.preprocessors:
            text = proc(text)
        
        # Translate
        result = self.translator.doubao_translate(text)
        
        # Apply postprocessors
        translated_text = result.text
        for proc in self.postprocessors:
            translated_text = proc(translated_text)
        
        return translated_text

# Usage example
pipeline = TranslationPipeline(translator)
pipeline.add_preprocessor(sanitize_text)
pipeline.add_preprocessor(lambda x: x.lower())
pipeline.add_postprocessor(lambda x: x.capitalize())
```

### Custom Cache Implementation
```python
from typing import Optional
import redis

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
    
    def get(self, key: str) -> Optional[str]:
        value = self.redis.get(key)
        return value.decode() if value else None
    
    def set(self, key: str, value: str, ttl: int = 3600):
        self.redis.setex(key, ttl, value)
    
    def delete(self, key: str):
        self.redis.delete(key)

# Usage
cache = RedisCache()
translator.set_cache(cache)
```

### Custom Metrics Collection
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_metric(self, name: str, value: float):
        self.metrics[name].append({
            'value': value,
            'timestamp': time.time()
        })
    
    def get_statistics(self, name: str) -> Dict[str, float]:
        values = [m['value'] for m in self.metrics[name]]
        return {
            'avg': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }

# Usage
metrics = MetricsCollector()
translator.set_metrics_collector(metrics)
```

## Contributing

### Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/doubaotrans.git
   cd doubaotrans
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_translation.py

# Run with coverage
pytest --cov=doubaotrans tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public methods
- Keep methods focused and concise

### Pull Request Process
1. Create a feature branch
2. Write tests for new features
3. Update documentation
4. Submit pull request

## License

MIT License. See [LICENSE](LICENSE) file for details. 

## Additional Resources

### Community & Support
- [GitHub Issues](https://github.com/yourusername/doubaotrans/issues)
- [Documentation](https://doubaotrans.readthedocs.io/)
- [Discord Community](https://discord.gg/doubaotrans)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/doubaotrans)

### Examples & Tutorials
1. Basic Usage Examples
   - [Quick Start Guide](docs/quickstart.md)
   - [Common Use Cases](docs/use-cases.md)
   - [Configuration Examples](docs/configuration.md)

2. Advanced Tutorials
   - [Custom Pipeline Development](docs/custom-pipeline.md)
   - [Performance Optimization](docs/performance.md)
   - [Error Handling Strategies](docs/error-handling.md)

3. Integration Examples
   - [Web Framework Integration](docs/web-integration.md)
   - [CLI Tool Development](docs/cli-development.md)
   - [Service Integration](docs/service-integration.md)

### API Documentation
- [Full API Reference](https://doubaotrans.readthedocs.io/api/)
- [OpenAPI Specification](docs/openapi.yaml)
- [API Changelog](docs/api-changelog.md)

## Acknowledgments

### Contributors
- List of contributors can be found in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Special thanks to the open source community

### Third-Party Libraries
- OpenAI API
- httpx
- tenacity
- python-dotenv
- And other dependencies listed in requirements.txt

### Inspiration
This project was inspired by and builds upon:
- OpenAI's GPT models
- Various open source translation tools
- Community feedback and contributions 