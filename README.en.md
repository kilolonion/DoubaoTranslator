# DoubaoTranslator: Professional Translation Toolkit Based on Doubao API

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.2-green.svg)](https://pypi.org/project/doubaotrans/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)

[中文](README.md) | English

DoubaoTranslator is a professional translation toolkit based on Doubao API, providing features such as multilingual translation, glossary management, context-aware translation, and style customization.

## Features

- **Multilingual Support**: Translation between 17 mainstream languages
- **Context-Aware Translation**: Maintains semantic coherence with context window
- **Glossary Management**: Custom terminology mapping for professional accuracy
- **Style Templates**: Predefined styles (formal, casual, technical, creative)
- **Streaming Translation**: Real-time translation with partial results
- **Batch Processing**: Efficient bulk translation with concurrency control
- **Enhanced Language Detection**: Combined results from multiple detectors
- **Performance Optimization**: Caching, retry mechanisms, HTTP/2 support
- **Document Translation**: Context-aware translation for long documents
- **Translation Evaluation**: Quality assessment functionality
- **Async Support**: Complete async operation support, including context managers

## Installation

```bash
pip install doubaotrans
```

## API Documentation

### Getting API Credentials

Before using DoubaoTranslator, you need to obtain API credentials from Volcengine. Follow these steps carefully:

1. Register and Login:
   - Visit [Volcengine Console](https://console.volcengine.com/)
   - Create an account if you haven't already

2. Get API Key:
   - Open the [API Key Management](https://console.volcengine.com/iam/keymanage/) page
   - Click "Create API Key"
   - (Optional) Switch project space if you're using a shared account
   - Enter a name for your API Key
   - Save the API Key securely - it will be used for authentication

3. Enable Doubao Model Service:
   - Go to "Volcengine AI Platform" in the console
   - Enable the Doubao model service
   - Note: Keep your API Key confidential to prevent security risks or financial losses

4. Create Inference Endpoint:
   - Go to "Model Access" page
   - Click "Create Inference Endpoint"
   - Select desired model (e.g., Doubao-pro-32k)
   - Configure parameters as needed
   - Save the Endpoint ID

For detailed information, please refer to [API Key Management](https://console.volcengine.com/iam/keymanage/).

Never share your API Key publicly or include it in version control systems.

### Getting API Credentials

Before using DoubaoTranslator, you need to obtain API credentials from Volcengine:

1. Register and Login:
   - Visit [Volcengine Console](https://console.volcengine.com/)
   - Create an account if you haven't already

2. Get API Key:
   - Navigate to "API Key Management" in the console
   - Click "Create API Key" to generate new credentials
   - Save your Access Key ID and Secret Access Key

3. Enable Doubao Model Service:
   - Go to "Volcengine AI Platform" in the console
   - Enable the Doubao model service

4. Create Inference Endpoint:
   - Go to "Model Access" page
   - Click "Create Inference Endpoint"
   - Select desired model (e.g., Doubao-pro-32k)
   - Configure parameters as needed
   - Save the Endpoint ID

Keep these credentials secure and never share them publicly.

### Initialization Options

```python
DoubaoTranslator(
    api_key: str = None,                    # API key (required)
    model_name: str = None,                 # Model name (optional)
    base_url: str = None,                   # API base URL (optional)
    max_workers: int = 5,                   # Max concurrent workers (optional)
    glossary_path: str = None,              # Glossary file path (optional)
    performance_mode: str = 'balanced',      # Performance mode (optional): 'fast', 'balanced', 'accurate'
    **kwargs                                # Other performance parameters (optional)
)
```

### Translation Methods

#### Basic Translation
```python
async def doubao_translate(
    text: Union[str, List[str]],           # Text or list of texts to translate
    dest: str = 'en',                      # Target language (required)
    src: str = 'auto',                     # Source language (optional, auto-detect by default)
    stream: bool = False                   # Whether to use streaming translation (optional)
) -> Union[DoubaoTranslated, List[DoubaoTranslated], AsyncGenerator]
```

#### Batch Translation
```python
async def translate_batch(
    texts: List[str],                      # List of texts to translate
    dest: str = 'en',                      # Target language
    src: str = 'auto',                     # Source language
    batch_size: int = 10                   # Batch size
) -> List[DoubaoTranslated]
```

#### Context-Aware Translation
```python
async def translate_with_context(
    text: str,                             # Text to translate
    context: str,                          # Context information
    dest: str = 'en',                      # Target language
    src: str = 'auto',                     # Source language
    style_guide: str = None                # Style guide
) -> DoubaoTranslated
```

#### Document Translation
```python
async def translate_document_with_context(
    paragraphs: List[str],                 # List of paragraphs
    dest: str = 'en',                      # Target language
    src: str = 'auto',                     # Source language
    context_window: int = 2,               # Context window size
    batch_size: int = 5,                   # Batch size
    style_guide: str = None                # Style guide
) -> List[DoubaoTranslated]
```

#### Style-Based Translation
```python
async def translate_with_style(
    text: str,                             # Text to translate
    dest: str = 'en',                      # Target language
    src: str = 'auto',                     # Source language
    style: Union[str, Dict] = 'formal',    # Translation style
    context: str = None,                   # Context information
    max_versions: int = 3                  # Maximum versions (for creative style)
) -> DoubaoTranslated
```

### Language Detection

#### Basic Detection
```python
async def doubao_detect(
    text: str                              # Text to detect
) -> DoubaoDetected
```

#### Enhanced Detection
```python
async def doubao_detect_enhanced(
    text: str                              # Text to detect
) -> DoubaoDetected
```

### Glossary Management

```python
def load_glossary(
    path: Union[str, Path]                 # Glossary file path
) -> None

def save_glossary(
    path: Union[str, Path]                 # Save path
) -> None

def add_term(
    term_id: str,                          # Term ID
    translations: Dict[str, str]           # Translations for each language
) -> None

async def apply_glossary(
    text: str,                             # Text to translate
    src: str,                              # Source language
    dest: str                              # Target language
) -> DoubaoTranslated
```

### Translation Evaluation

```python
async def evaluate_translation(
    original: str,                         # Original text
    translated: str,                       # Translated text
    src: str,                             # Source language
    dest: str                             # Target language
) -> Dict[str, float]                     # Returns evaluation metrics
```

### Performance Configuration

#### Predefined Performance Modes
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

#### Custom Performance Settings
```python
def set_performance_config(
    max_workers: int = None,               # Maximum concurrent workers
    cache_ttl: int = None,                 # Cache time-to-live
    min_request_interval: float = None,     # Minimum request interval
    max_retries: int = None,               # Maximum retry attempts
    timeout: int = None,                   # Request timeout
    temperature: float = None,             # Sampling temperature
    max_tokens: int = None                 # Maximum tokens
) -> None
```

### Style Templates

```python
style_templates = {
    'formal': """
        Translation Requirements:
        1. Use formal academic language
        2. Maintain rigorous sentence structure
        3. Use standard professional terminology
        4. Avoid colloquialisms and simplified expressions
    """,
    'casual': """
        Translation Requirements:
        1. Use everyday conversational language
        2. Keep language natural and flowing
        3. Use short sentences
        4. Common abbreviations are allowed
    """,
    'technical': """
        Translation Requirements:
        1. Strictly use technical terminology
        2. Maintain professional accuracy
        3. Use standardized technical expressions
        4. Maintain terminology consistency
    """,
    'creative': """
        Translation Requirements:
        1. Provide multiple different translation versions
        2. Use different expressions for each version
        3. Maintain the core meaning of the original text
        4. Limit to specified number of versions
    """
}
```

### Utility Methods

```python
async def test_connection() -> bool        # Test API connection
def get_config() -> dict                   # Get current configuration
def get_supported_languages() -> List[str]  # Get list of supported languages
def is_language_supported(
    lang_code: str                         # Language code
) -> bool                                  # Check if language is supported
```

### Async Context Manager Support

```python
async with DoubaoTranslator(api_key="your_api_key") as translator:
    result = await translator.doubao_translate("Hello", dest="zh")
```

### Return Objects

#### DoubaoTranslated
```python
class DoubaoTranslated:
    src: str          # Source language code
    dest: str         # Destination language code
    origin: str       # Original text
    text: str         # Translated text
    pronunciation: str # Pronunciation (if available)
```

#### DoubaoDetected
```python
class DoubaoDetected:
    lang: str         # Detected language code
    confidence: float # Detection confidence (0.00 to 1.00)
    details: dict     # Additional detection details (for enhanced detection)
```

### Exception Classes

```python
class DoubaoError(Exception)                    # Base exception class
class DoubaoAuthenticationError(DoubaoError)    # Authentication errors
class DoubaoConnectionError(DoubaoError)        # Connection errors
class DoubaoAPIError(DoubaoError)              # API-related errors
class DoubaoConfigError(DoubaoError)           # Configuration errors
class DoubaoValidationError(DoubaoError)       # Input validation errors
```

## Usage Examples

### Basic Translation
```python
translator = DoubaoTranslator(api_key="your_api_key")

# Single text translation
result = await translator.doubao_translate("Hello, World!", dest="zh")
print(result.text)  # 你好，世界！

# Batch translation
texts = ["Hello", "World", "AI"]
results = await translator.translate_batch(texts, dest="zh")
for result in results:
    print(f"{result.origin} -> {result.text}")
```

### Context-Aware Translation
```python
# Document translation
paragraphs = [
    "This is the first paragraph about AI development.",
    "This is the second paragraph discussing AI technology.",
    "The final paragraph summarizes the future of AI."
]

results = await translator.translate_document_with_context(
    paragraphs=paragraphs,
    dest="zh",
    context_window=2,
    style_guide="academic"
)

for result in results:
    print(result.text)
```

### Style-Based Translation
```python
# Using predefined style
formal_result = await translator.translate_with_style(
    text="Hello",
    dest="zh",
    style="formal"
)

# Using custom style
custom_style = {
    "tone": "formal",
    "expression": "concise",
    "professionalism": "high"
}
custom_result = await translator.translate_with_style(
    text="Hello",
    dest="zh",
    style=custom_style
)
```

### Translation Evaluation
```python
scores = await translator.evaluate_translation(
    original="Hello, World!",
    translated="你好，世界！",
    src="en",
    dest="zh"
)
print(f"Accuracy: {scores['accuracy']}")
print(f"Fluency: {scores['fluency']}")
print(f"Professionalism: {scores['professionalism']}")
print(f"Style: {scores['style']}")
```

## Notes

1. API Limitations
   - Maximum text length per request: 5000 characters
   - API rate limiting may apply
   - Async methods recommended for handling large volumes

2. Performance Optimization
   - HTTP/2 support requires the `hyper` package
   - Caching mechanism reduces duplicate requests
   - Batch processing improves efficiency

3. Error Handling
   - All async methods should use try-except for error handling
   - Network errors are automatically retried
   - Authentication errors require API key verification

4. Best Practices
   - Use async context managers for automatic resource management
   - Choose appropriate performance mode
   - Set reasonable context window size
   - Save glossary regularly

## Disclaimer

1. This project is an unofficial wrapper based on the Doubao API and is not affiliated with Doubao.
2. To use this project, you need to apply for a Doubao API key and comply with Doubao's terms of service.
3. The copyrights of the third-party libraries used in this project belong to their original authors.

## Dependency Declaration

This project uses the following open-source projects:
- aiohttp (Apache 2.0)
- httpx (BSD)
- openai (MIT)
- tenacity (Apache 2.0)

## License

This project is open-sourced under the MIT License.
