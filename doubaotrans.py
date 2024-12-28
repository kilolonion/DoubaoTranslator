import os
from dotenv import load_dotenv
import openai
from typing import List, Union, Dict, Optional, Tuple, Any
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langdetect import detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from pathlib import Path
import re
import uuid
import asyncio
import aiohttp
import httpx
try:
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet

# 首先定义常量
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "ep-20241114093010-dm56w"
MAX_RETRIES = 3
MAX_WORKERS = 5  # 并发线程数

# 在常量定义部分添加性能配置
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

# 然后配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DoubaoTranslator')

# 设置langdetect的随机种子，确保结果一致性
DetectorFactory.seed = 0

# 从环境变量加载配置
ENV_CONFIG = {
    'API_KEY': None,
    'BASE_URL': None,
    'MODEL': None
}

try:
    # 尝试加载 .env 文件
    load_dotenv()
    
    # 读取配置项
    ENV_CONFIG['API_KEY'] = os.getenv('ARK_API_KEY')
    ENV_CONFIG['BASE_URL'] = os.getenv('ARK_BASE_URL', DEFAULT_BASE_URL)
    ENV_CONFIG['MODEL'] = os.getenv('ARK_MODEL', DEFAULT_MODEL)
    
    if ENV_CONFIG['API_KEY']:
        logger.info("Successfully loaded API key from environment")
    if ENV_CONFIG['BASE_URL'] != DEFAULT_BASE_URL:
        logger.info(f"Using custom base URL: {ENV_CONFIG['BASE_URL']}")
    if ENV_CONFIG['MODEL'] != DEFAULT_MODEL:
        logger.info(f"Using custom model: {ENV_CONFIG['MODEL']}")
        
except Exception as e:
    logger.warning(f"Error loading .env configuration: {str(e)}")

# 语言代码映射表
LANG_CODE_MAP = {
    # ISO 639-1 到豆包语言代码的映射
    'zh-cn': 'zh', 'zh-tw': 'zh', 'zh': 'zh',
    'en': 'en',
    'ja': 'ja',
    'ko': 'ko',
    'fr': 'fr',
    'es': 'es',
    'ru': 'ru',
    'de': 'de',
    'it': 'it',
    'tr': 'tr',
    'pt': 'pt',
    'vi': 'vi',
    'id': 'id',
    'th': 'th',
    'ms': 'ms',
    'ar': 'ar',
    'hi': 'hi'
}

class DoubaoTranslated:
    """表示豆包翻译结果的类"""
    def __init__(self, src, dest, origin, text, pronunciation=None):
        self.src = src
        self.dest = dest
        self.origin = origin
        self.text = text
        self.pronunciation = pronunciation

    def __repr__(self):
        return f'<DoubaoTranslated src={self.src} dest={self.dest} text={self.text} pronunciation={self.pronunciation}>'

class DoubaoDetected:
    """表示豆包语言检测结果的类"""
    def __init__(self, lang: str, confidence: float, details: Dict = None):
        self.lang = self._normalize_lang_code(lang)
        self.confidence = confidence
        self.details = details or {}

    def _normalize_lang_code(self, lang: str) -> str:
        """标准化语言代码"""
        return LANG_CODE_MAP.get(lang.lower(), lang.lower())

    def __repr__(self):
        if self.details:
            return f'<DoubaoDetected lang={self.lang} confidence={self.confidence:.3f} details={self.details}>'
        return f'<DoubaoDetected lang={self.lang} confidence={self.confidence:.3f}>'

class DoubaoTranslationError(Exception):
    """豆包翻译错误基类"""
    pass

class DoubaoAPIError(DoubaoTranslationError):
    """API错误"""
    pass

class DoubaoAuthenticationError(DoubaoTranslationError):
    """认证错误"""
    pass

class DoubaoConnectionError(DoubaoTranslationError):
    """连接错误"""
    pass

class PerformanceMetrics:
    def __init__(self):
        self.request_times = []
        self.request_sizes = []
        self.error_counts = {}
        self.last_cleanup = time.time()
    
    def add_request(self, duration: float, size: int):
        self.request_times.append((time.time(), duration))
        self.request_sizes.append(size)
        self._cleanup_old_metrics()
    
    def add_error(self, error_type: str):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def _cleanup_old_metrics(self):
        if time.time() - self.last_cleanup > 3600:  # 每小时清理
            cutoff = time.time() - 86400  # 保留24小时的数据
            self.request_times = [(t, d) for t, d in self.request_times if t > cutoff]
            self.last_cleanup = time.time()
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            'average_response_time': sum(d for _, d in self.request_times) / len(self.request_times) if self.request_times else 0,
            'total_requests': len(self.request_times),
            'error_rates': {k: v/len(self.request_times) for k, v in self.error_counts.items()},
            'average_request_size': sum(self.request_sizes) / len(self.request_sizes) if self.request_sizes else 0
        }

class DoubaoTranslator:
    """豆包AI翻译器类"""

    def __init__(self, api_key=None, model_name=None, base_url=None, 
                 max_workers=MAX_WORKERS, glossary_path=None,
                 performance_mode='balanced', **kwargs):
        """
        初始化DoubaoTranslator对象。

        :param api_key: 豆包API密钥
        :param model_name: 豆包模型名称
        :param base_url: 豆包API的基础URL
        :param max_workers: 最大并发线程数
        :param glossary_path: 术语表文件路径
        :param performance_mode: 性能模式('fast', 'balanced', 'accurate')
        :param kwargs: 自定义性能参数
        """
        # 确保环境变量已加载
        load_dotenv()
        
        # 验证API密钥
        self.api_key = api_key or os.getenv('ARK_API_KEY')
        if not self.api_key:
            raise ValueError("API密钥未提供。请通过参数传入api_key或设置环境变量 ARK_API_KEY")
        
        # 验证API密钥格式
        if not isinstance(self.api_key, str) or len(self.api_key) < 32:
            raise ValueError("API密钥格式无效")
            
        # 设置基础URL和模型
        self.base_url = base_url or os.getenv('ARK_BASE_URL', DEFAULT_BASE_URL)
        self.model = model_name or os.getenv('ARK_MODEL', DEFAULT_MODEL)
        
        # 验证性能模式
        if performance_mode not in PERFORMANCE_PROFILES:
            raise ValueError(f"无效的性能模式。必须是: {', '.join(PERFORMANCE_PROFILES.keys())}")
        
        # 加载性能配置
        self.perf_config = PERFORMANCE_PROFILES[performance_mode].copy()
        # 允许通过kwargs覆盖特定配置
        self.perf_config.update(kwargs)
        
        # 应用性能配置
        self._cache_ttl = self.perf_config['cache_ttl']
        self._min_request_interval = self.perf_config['min_request_interval']
        self.max_retries = self.perf_config['max_retries']
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 其他初始化
        self._last_request_time = 0
        self._response_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.system_prompt = "你是豆包翻译助手，请直接翻译用户的文本，不要添加任何解释。"
        
        # 初始化术语表
        self.glossary: Dict[str, Dict[str, str]] = {}
        if glossary_path:
            self.load_glossary(glossary_path)
        
        logger.info(f"DoubaoTranslator initialized with model: {self.model} and base_url: {self.base_url}")

        # 添加默认风格模板
        self.style_templates = {
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
                1. 提供2-3个不同的翻译版本
                2. 每个版本���用不同的表达方式
                3. 保持原文的核心含义
                4. 限制在3个版本以内
            """
        }

        # 增加连接池和会话管理
        self.session = None
        self.semaphore = asyncio.Semaphore(max_workers)
        
        # 优化缓存设置
        self._response_cache = {}
        self._last_request_time = 0
        
        # 预热连接
        self._warmup_connection()

        self.metrics = PerformanceMetrics()

    def _warmup_connection(self):
        """预热连接以减少首次请求的延迟"""
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "warmup"}],
                max_tokens=1
            )
        except Exception:
            pass

    def _should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        if isinstance(exception, (openai.APIError, openai.APIConnectionError)):
            return True
        if isinstance(exception, httpx.ConnectError):
            return True
        return False

    def _get_retry_config(self):
        """获取重试配置"""
        return {
            'multiplier': self.perf_config.get('retry_multiplier', 0.5),
            'min': self.perf_config.get('retry_min_wait', 1),
            'max': self.perf_config.get('retry_max_wait', 4),
            'max_retries': self.perf_config.get('max_retries', 3)
        }

    @retry(
        stop=stop_after_attempt(3),  # 使用固定值
        wait=wait_exponential(multiplier=0.5, min=1, max=4),  # 使用固定值
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, httpx.ConnectError))
    )
    def _make_request(self, messages, stream=False):
        """改进的请求处理"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last_request)
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # 验证API密钥
            if not self.api_key:
                raise ValueError("API密钥未设置")

            # 添加请求日志
            logger.debug(f"Making request to {self.base_url} with API key: {self.api_key[:8]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=self.perf_config['temperature'],
                max_tokens=self.perf_config['max_tokens'],
                timeout=self.perf_config['timeout']
            )
            
            self._last_request_time = time.time()
            return response
            
        except openai.AuthenticationError as e:
            raise DoubaoAuthenticationError(f"认证失败: {str(e)}")
        except openai.APIConnectionError as e:
            raise DoubaoConnectionError(f"连接失败: {str(e)}")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request {request_id} failed after {duration:.2f}s: {str(e)}")
            raise DoubaoAPIError(f"API请求失败: {str(e)}")

    def _get_cache_key(self, messages):
        """生成缓存键"""
        # 只使用消息内容和角色生成缓存键
        key_parts = [f"{m['role']}:{m['content']}" for m in messages]
        return hash(tuple(key_parts))

    def _get_from_cache(self, key):
        """从缓存获取响应"""
        if key in self._response_cache:
            cached_item = self._response_cache[key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                return cached_item['response']
            else:
                del self._response_cache[key]
        return None

    def _add_to_cache(self, key, response):
        """添加响应到缓存"""
        self._response_cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # 清理过期缓存
        self._cleanup_cache()

    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self._response_cache.items()
            if current_time - v['timestamp'] > self._cache_ttl
        ]
        for k in expired_keys:
            del self._response_cache[k]

    async def _init_session(self):
        """初始化异步会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def _close_session(self):
        """关闭异步会话"""
        if self.session:
            await self.session.close()
            self.session = None

    async def translate_batch_async(self, texts: List[str], dest='en', src='auto', batch_size=5) -> List[DoubaoTranslated]:
        """异步批量翻译"""
        results = []
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                for text in batch:
                    task = asyncio.create_task(
                        self._doubao_translate_single_async(text, dest, src, session)
                    )
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend(batch_results)
        
        return results

    def translate_batch(self, texts: List[str], dest='en', src='auto', batch_size=5) -> List[DoubaoTranslated]:
        """优化的批量翻译实现"""
        results = []
        start_time = time.time()
        max_workers = self.perf_config.get('max_workers', MAX_WORKERS)
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            futures = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for text in batch:
                    future = executor.submit(self._doubao_translate_single, text, dest, src, False)
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Batch translation error: {str(e)}")
                        results.append(DoubaoTranslated(src, dest, text, str(e)))
        
        duration = time.time() - start_time
        logger.info(f"Batch translation completed in {duration:.2f}s - {len(texts)} texts")
        return results

    def load_glossary(self, path: Union[str, Path]) -> None:
        """
        加载术语表

        :param path: 术语表文件路径
        :raises: FileNotFoundError 如果文件不存在
        :raises: json.JSONDecodeError 如果JSON格式无效
        """
        try:
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"术语表文件不存在: {path}")
            
            with path.open('r', encoding='utf-8') as f:
                self.glossary = json.load(f)
            
            logger.info(f"Loaded glossary with {len(self.glossary)} terms from {path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in glossary file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading glossary: {e}")
            raise

    def save_glossary(self, path: Union[str, Path]) -> None:
        """
        保存术语表

        :param path: 保存路径
        """
        try:
            path = Path(path)
            with path.open('w', encoding='utf-8') as f:
                json.dump(self.glossary, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved glossary to {path}")
        except Exception as e:
            logger.error(f"Error saving glossary: {e}")
            raise

    def add_term(self, term_id: str, translations: Dict[str, str]) -> None:
        """
        加或更新术语

        :param term_id: 术语ID
        :param translations: 各语言的翻译
        """
        self.glossary[term_id] = translations
        logger.debug(f"Added/updated term: {term_id} with translations: {translations}")

    def apply_glossary(self, text: str, src: str, dest: str) -> DoubaoTranslated:
        """应用术语表进行翻译"""
        if not self.glossary:
            return self.doubao_translate(text, dest=dest, src=src)

        try:
            # 创建术语替换映射
            replacements = {}
            placeholder_format = "[[TERM_{}_]]"
            
            # 第一步：替换术语为占位符
            modified_text = text
            for term_id, translations in self.glossary.items():
                if src in translations and dest in translations:
                    source_term = translations[src]
                    target_term = translations[dest]
                    
                    # 避免重复替换
                    if source_term in modified_text:
                        placeholder = placeholder_format.format(term_id)
                        # 使用正则保完整词匹配，修复正则表达式
                        modified_text = re.sub(
                            r'\b' + re.escape(source_term) + r'\b',
                            placeholder,
                            modified_text
                        )
                        replacements[placeholder] = target_term

            # 第二步：翻译修改后的文本
            translated = self.doubao_translate(modified_text, dest=dest, src=src)
            result = translated.text

            # 第三步：还原术语
            for placeholder, term in replacements.items():
                result = result.replace(placeholder, term)
                # 修复括号处理的正则表达式
                result = re.sub(r'\(+([^()]+)\)+', r'(\1)', result)

            logger.debug(f"Applied glossary translation with {len(replacements)} terms")
            return DoubaoTranslated(src, dest, text, result)

        except Exception as e:
            logger.error(f"Error applying glossary: {e}")
            raise Exception(f"术语表应用失败: {str(e)}")

    def get_term(self, term_id: str) -> Optional[Dict[str, str]]:
        """
        获取术语的翻译

        :param term_id: 术语ID
        :return: 术语的翻译字典，如果不存在返回None
        """
        return self.glossary.get(term_id)

    def _doubao_translate_single(self, text: str, dest: str, src: str, stream: bool):
        """优化的单个文本翻译现"""
        try:
            # 1. 预理文本
            text = text.strip()
            if not text:
                return DoubaoTranslated(src, dest, text, text)

            # 2. 检查缓存
            cache_key = f"{text}:{src}:{dest}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

            # 3. 构建示词
            if src == 'auto':
                prompt = f"将以下文本翻译成{dest}：\n{text}"
            else:
                prompt = f"将以下{src}文本翻译成{dest}：\n{text}"

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            # 4. 发送请求并获响应
            response = self._make_request(messages, stream=stream)
            
            if stream:
                translated_text = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        translated_text += chunk.choices[0].delta.content
            else:
                translated_text = response.choices[0].message.content.strip()

            # 5. 创建结果对象
            result = DoubaoTranslated(
                src=src,
                dest=dest,
                origin=text,
                text=translated_text
            )

            # 6. 缓存结果
            self._add_to_cache(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Translation failed for text: {text[:50]}... Error: {str(e)}")
            raise Exception(f"翻译失败: {str(e)}")

    def doubao_translate(self, text: Union[str, List[str]], dest='en', src='auto', stream=False):
        """
        翻译文本，支持批量处理

        :param text: 要翻译的源文本（字符串或字符串列表）
        :param dest: 目标语言
        :param src: 源语言
        :param stream: 是否使用流式翻译
        :return: 翻译结果
        """
        if isinstance(text, list):
            return self.translate_batch(text, dest, src)
        return self._doubao_translate_single(text, dest, src, stream)

    def _normalize_detection_result(self, detected_text: str) -> str:
        """规范化语言检测结果"""
        # 处理直接返回语言代码的情况
        if len(detected_text) <= 3:
            return detected_text.lower()
        
        # 处理返回描述文本的情况
        lang_patterns = {
            r'.*韩语.*': 'ko',
            r'.*法语.*': 'fr',
            r'.*中文.*': 'zh',
            r'.*英语.*': 'en',
            r'.*日语.*': 'ja',
            r'.*俄语.*': 'ru',
            r'.*德语.*': 'de',
            r'.*阿拉伯语.*': 'ar'
        }
        
        for pattern, code in lang_patterns.items():
            if re.search(pattern, detected_text):
                return code
        
        return detected_text.lower()

    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
    def doubao_detect(self, text: str) -> DoubaoDetected:
        """
        检测文本语言

        :param text: 要检测语言的文本
        :return: DoubaoDetected对象
        """
        try:
            messages = [
            {"role": "system", "content": "你是豆包语言检测助手，请只返回检测到的语言代码，例如：en、zh、ja等"},
            {"role": "user", "content": f"检测下面文本的语言：\n{text}"}
        ]

            response = self._make_request(messages)
            detected_lang = self._normalize_detection_result(response.choices[0].message.content.strip())
            return DoubaoDetected(detected_lang, 1.0)

        except Exception as e:
            logger.error(f"Language detection failed for text: {text[:50]}... Error: {str(e)}")
            raise

    @lru_cache(maxsize=1000)
    def _cached_detect(self, text: str) -> Tuple[str, float]:
        doubao_result = self.doubao_detect(text)
        return doubao_result.lang, doubao_result.confidence

    def doubao_detect_enhanced(self, text: str) -> DoubaoDetected:
        """
        增强的语言检测功能，结合多个检测器的结果

        :param text: 要检测语言的文本
        :return: DoubaoDetected对象，包含检测结果和置信度
        """
        try:
            # 初始化结果字典
            lang_scores: Dict[str, float] = {}
            
            # 1. 使用豆包API检测
            try:
                doubao_lang, doubao_confidence = self._cached_detect(text)
                lang_scores[doubao_lang] = doubao_confidence * 1.2  # 给包结果更高权重
                logger.debug(f"Doubao detection: {doubao_lang} ({doubao_confidence})")
            except Exception as e:
                logger.warning(f"Doubao detection failed: {str(e)}")

            # 2. 使用langdetect检测
            try:
                langdetect_results = detect_langs(text)
                for result in langdetect_results:
                    normalized_lang = LANG_CODE_MAP.get(result.lang, result.lang)
                    current_score = lang_scores.get(normalized_lang, 0)
                    lang_scores[normalized_lang] = current_score + result.prob
                    logger.debug(f"Langdetect detection: {normalized_lang} ({result.prob})")
            except LangDetectException as e:
                logger.warning(f"Langdetect detection failed: {str(e)}")

            # 3. 如果没有得到任何结果
            if not lang_scores:
                raise ValueError("No language detection results available")

            # 4. 找出得分最高的语言
            best_lang, best_score = max(lang_scores.items(), key=lambda x: x[1])
            
            # 5. 计算置信度得分（归一化到0-1范围）
            total_score = sum(lang_scores.values())
            confidence = best_score / total_score if total_score > 0 else 0

            # 6. 返回增强的语言检测结果
            return DoubaoDetected(
                lang=best_lang,
                confidence=confidence,
                details={
                    'raw_scores': lang_scores,
                    'detection_methods': {
                        'doubao': bool('doubao_lang' in locals()),
                        'langdetect': bool('langdetect_results' in locals())
                    }
                }
            )

        except Exception as e:
            logger.error(f"Enhanced language detection failed: {str(e)}")
            raise Exception(f"语  检测失败: {str(e)}")

    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言列表

        :return: 支持的语言代码列表
        """
        return list(DOUBAO_LANGUAGES.keys())

    def is_language_supported(self, lang_code: str) -> bool:
        """
        检查语言是否被支持

        :param lang_code: 语言代码
        :return: 是否支持该语言
        """
        normalized_code = LANG_CODE_MAP.get(lang_code.lower(), lang_code.lower())
        return normalized_code in DOUBAO_LANGUAGES

    def __del__(self):
        """确保资源正确释放"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        if hasattr(self, 'session') and self.session:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._close_session())
            else:
                loop.run_until_complete(self._close_session())

    def translate_with_context(self, text: str, context: str, dest='en', src='auto', style_guide=None) -> DoubaoTranslated:
        """
        带上下文的翻译，支持风格指南和一致性控制

        :param text: 要翻译的文本
        :param context: 上下文信息
        :param dest: 目标语言
        :param src: 源语言（auto为自动检测）
        :param style_guide: 风格指南（可选）
        :return: DoubaoTranslated对象
        """
        try:
            # 1. 如果语言auto，先进行语言检测
            if src == 'auto':
                detected = self.doubao_detect_enhanced(text)
                src = detected.lang
                logger.debug(f"Detected source language: {src}")

            # 2. 构建提示词
            style_instructions = ""
            if style_guide:
                style_instructions = f"\n\n风格要求：\n{style_guide}"

            prompt = f"""请在理解以下上下文的基础上，将文本从{src}翻译成{dest}：

上下文背景：
{context}

需要翻译的文本：
{text}

翻译要求：
1. 保持与上下文的连贯性和一致性
2. 保留专业术语准确性
3. 保持原文的语气和风格
4. 保代词指代的正确性
5. 注意上下文中的特定含义{style_instructions}

请直接返回翻译结果，不要添加任何解释。"""

            # 3. 应用术语表（如果有）
            if self.glossary:
                logger.debug("Applying glossary before context translation")
                glossary_result = self.apply_glossary(text, src, dest)
                text = glossary_result.text

            # 4. 发送翻译请求
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self._make_request(messages, stream=False)
            translated_text = response.choices[0].message.content.strip()

            # 5. 记录翻译结果
            logger.info(f"Context-aware translation completed for text length: {len(text)}")
            logger.debug(f"Translation context length: {len(context)}")

            return DoubaoTranslated(
                src=src,
                dest=dest,
                origin=text,
                text=translated_text,
            )

        except Exception as e:
            logger.error(f"Context-aware translation failed: {str(e)}")
            raise Exception(f"上下文感知翻译失败: {str(e)}")

    def translate_document_with_context(self, 
                                     paragraphs: List[str], 
                                     dest='en', 
                                     src='auto', 
                                     context_window: int = 2,
                                     batch_size: int = 5) -> List[DoubaoTranslated]:
        """
        翻译整个文档，使用滑动窗口保持上下文连贯性

        :param paragraphs: 段落列表
        :param dest: 目标语言
        :param src: 源语言
        :param context_window: 上下文窗口大小（前后考虑几个段落）
        :param batch_size: 批处理大小
        :return: 翻译结果列表
        """
        results = []
        total_paragraphs = len(paragraphs)

        for i in range(0, total_paragraphs, batch_size):
            batch = paragraphs[i:i+batch_size]
            batch_results = []

            for j, current_para in enumerate(batch):
                global_index = i + j
                start_idx = max(0, global_index - context_window)
                end_idx = min(total_paragraphs, global_index + context_window + 1)
                
                context_paras = paragraphs[start_idx:global_index] + paragraphs[global_index+1:end_idx]
                context = "\n".join(context_paras)

                batch_results.append(self.translate_with_context(
                    text=current_para,
                    context=context,
                    dest=dest,
                    src=src
                ))

            results.extend(batch_results)

        return results

    def add_style_template(self, name: str, template: str) -> None:
        """
        添加新的风格模板

        :param name: 模板名称
        :param template: 模板内容
        """
        self.style_templates[name] = template
        logger.info(f"Added new style template: {name}")

    def get_style_template(self, name: str) -> str:
        """
        获取风格模板

        :param name: 模板名称
        :return: 模板内容
        """
        return self.style_templates.get(name)

    def _format_creative_translation(self, text: str) -> str:
        """格式化创意翻译结果"""
        # 取实际的翻译内容
        translations = []
        for line in text.split('\n'):
            # 移除版本标记、序号等
            line = line.strip()
            if not line or line.startswith('版本') or line.startswith('以下') or line == '-':
                continue
            # 移除序号和折号
            line = re.sub(r'^[-\d\.\s]+', '', line.strip())
            if line:
                translations.append(line)
        
        # 限制版本数量并用分号连接
        return ' ; '.join(translations[:3])

    def _format_translation_result(self, text: str, style: str) -> str:
        """格式化翻译结果"""
        if style == 'creative':
            return self._format_creative_translation(text)
        return text.strip()

    def validate_style(self, style: Union[str, Dict[str, str]]) -> Tuple[bool, str]:
        """
        验证翻译风格的有效性

        :param style: 风格名称或自定义风格配置
        :return: (是否有效, 建议或错误信息)
        """
        if isinstance(style, str):
            if style in self.style_templates:
                return True, "风格有效"
            return False, f"未知的风格名称。可用风格: {', '.join(self.style_templates.keys())}"
        
        if isinstance(style, dict):
            required_keys = {'语气', '表达方式', '专业程度'}
            missing_keys = required_keys - set(style.keys())
            if missing_keys:
                return False, f"自定义风格缺少必要的配置项: {', '.join(missing_keys)}"
            return True, "自定义风格配置有效"
        
        return False, "风格必须是预定义名称或配置字典"

    def translate_with_style(self, text: str, dest: str = 'en', src: str = 'auto', 
                            style: Union[str, Dict] = 'formal', context: str = None,
                            max_versions: int = 3) -> DoubaoTranslated:
        """
        带风格的翻译

        :param text: 要翻译的文本
        :param dest: 目标语言
        :param src: 源语言
        :param style: 翻译风格，可以是预定义风格的名称或自定义风格字典
        :param context: 上下文信息
        :param max_versions: 创意风格时的最大版本数量，默认3个
        :return: DoubaoTranslated对象
        """
        start_time = time.time()
        try:
            # 构建提示信息
            if isinstance(style, str):
                if style not in self.style_templates:
                    raise ValueError(f"未知的预定义风格: {style}")
                style_prompt = self.style_templates[style]
                if style == 'creative':
                    # 动态更新创意风格的版本数限制
                    style_prompt = f"""
                    翻译要求：
                    1. 提供{max_versions}个不同的翻译版本
                    2. 每个版本使用不同的表达方式
                    3. 保持原文的核心含义
                    4. 限制在{max_versions}个版本以内
                    """
            else:
                # 将自定义风格字典转换为提示文本
                style_prompt = "翻译要求：\n" + "\n".join([f"{k}: {v}" for k, v in style.items()])

            # 添加上下文信息（如果有）
            context_part = f"\n相关上下文：\n{context}\n" if context else ""

            messages = [
                {"role": "system", "content": "你是一个专业的翻译助手，请按照指定的风格要求进行翻译。"},
                {"role": "user", "content": f"""
{style_prompt}

{context_part}
需要翻译的文本：
{text}

请直接提供翻译结果，不要添加任何解释。如果是创意风格，最���提供{max_versions}个不同的版本，用分号分隔。
"""}
            ]

            response = self._make_request(messages, stream=False)
            translated_text = response.choices[0].message.content.strip()

            duration = time.time() - start_time
            logger.info(f"Styled translation completed in {duration:.2f}s - Style: {style}, Length: {len(text)}, Languages: {src}->{dest}")

            return DoubaoTranslated(
                src=src,
                dest=dest,
                origin=text,
                text=translated_text
            )

        except Exception as e:
            logger.error(f"Style translation failed: {str(e)}")
            raise Exception(f"风格化翻译失败: {str(e)}")

    def evaluate_translation(self, original: str, translated: str, src: str, dest: str) -> Dict[str, float]:
        """
        评估翻译质量
        
        :return: 包含各项指标的字典
        """
        prompt = f"""请评估以下翻译的质量，给出0-1的分数：

原文 ({src}): {original}
译文 ({dest}): {translated}

请从以下几个方面评分：
1. 准确性：内容是否准确传达
2. 流畅性：是否自流畅
3. 专业性：专业术语使用是否恰当
4. 风格：是否保持原文风格

只返回JSON式的评分结果。"""

        try:
            messages = [
                {"role": "system", "content": "你是翻译质量评估专家"},
                {"role": "user", "content": prompt}
            ]
            
            response = self._make_request(messages)
            scores = json.loads(response.choices[0].message.content)
            return scores

        except Exception as e:
            logger.error(f"Translation evaluation failed: {str(e)}")
            return {
                "accuracy": 0.0,
                "fluency": 0.0,
                "professionalism": 0.0,
                "style": 0.0
            }

    @lru_cache(maxsize=1000)
    def _get_cached_translation(self, text: str, dest: str, src: str, style: str = None) -> str:
        """获取缓存的翻译结果"""
        cache_key = f"{text}:{src}:{dest}:{style}"
        return cache_key

    def set_performance_config(self, **kwargs):
        """
        动态更新性能配置

        :param kwargs: 要更新的性能参数
        """
        self.perf_config.update(kwargs)
        # 更新相关实例变量
        if 'cache_ttl' in kwargs:
            self._cache_ttl = kwargs['cache_ttl']
        if 'min_request_interval' in kwargs:
            self._min_request_interval = kwargs['min_request_interval']
        if 'max_retries' in kwargs:
            self.max_retries = kwargs['max_retries']

    def test_connection(self) -> bool:
        """
        测试API连接和认证

        :return: 连接测试是否成功
        """
        try:
            response = self._make_request([
                {"role": "system", "content": "test"},
                {"role": "user", "content": "test"}
            ])
            logger.info("API连接测试成功")
            return True
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return False

    def get_config(self) -> dict:
        """
        获取当前配置信息

        :return: 包含所有配置信息的字典
        """
        return {
            'api_key': f"{self.api_key[:8]}...",  # 只显示前8位
            'base_url': self.base_url,
            'model': self.model,
            'performance_config': self.perf_config,
            'cache_ttl': self._cache_ttl,
            'min_request_interval': self._min_request_interval,
            'max_retries': self.max_retries
        }

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置参数"""
        required_fields = {
            'max_retries': (int, lambda x: x > 0),
            'cache_ttl': (int, lambda x: x > 0),
            'max_tokens': (int, lambda x: 0 < x <= 2048),
            'temperature': (float, lambda x: 0 <= x <= 1),
        }
        
        for field, (field_type, validator) in required_fields.items():
            value = config.get(field)
            if not isinstance(value, field_type):
                raise ValueError(f"{field} must be of type {field_type.__name__}")
            if not validator(value):
                raise ValueError(f"Invalid value for {field}: {value}")

# 豆包支持的语言代码常量
DOUBAO_LANGUAGES = {
    'zh': 'chinese',
    'en': 'english',
    'ja': 'japanese',
    'ko': 'korean',
    'fr': 'french',
    'es': 'spanish',
    'ru': 'russian',
    'de': 'german',
    'it': 'italian',
    'tr': 'turkish',
    'pt': 'portuguese',
    'vi': 'vietnamese',
    'id': 'indonesian',
    'th': 'thai',
    'ms': 'malay',
    'ar': 'arabic',
    'hi': 'hindi'
}

# 使用示例
if __name__ == "__main__":
    # 从环境变量获取API密钥
    api_key = os.getenv('ARK_API_KEY')
    if not api_key:
        print("请设置环境变量 ARK_API_KEY")
        exit(1)
        
    # 创建豆包翻译器实例
    doubao_translator = DoubaoTranslator(
        api_key=api_key,  # 使用环境变量中的API密钥
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )

    # 基本法
    print("\n----- 豆包基本翻译 -----")
    result = doubao_translator.doubao_translate('你好，世界！', dest='en')
    print(result)

    # 指定源语言
    print("\n----- 豆包指定源语言翻译 -----")
    result = doubao_translator.doubao_translate('Hello, world!', src='en', dest='zh')
    print(result)

    # 流式翻译
    print("\n----- 豆包流式翻译 -----")
    result = doubao_translator.doubao_translate('你好，世界！', dest='en', stream=True)
    print(result)

    # 批量翻译
    print("\n----- 豆包批量翻译 -----")
    texts = ['你好', '世界', '人工智能']
    results = doubao_translator.doubao_translate(texts, dest='en')
    for result in results:
        print(f"{result.origin} -> {result.text}")

    # 语言检测
    print("\n----- 豆包语言检测 -----")
    detection = doubao_translator.doubao_detect('这是一个中文句子')
    print(detection)
    detection = doubao_translator.doubao_detect('This is an English sentence')
    print(detection)

    # 增强的语言检测测试
    print("\n----- 增强的语言检测 -----")
    test_texts = [
        "这是一个中文句子，来试语言检测功能。",
        "This is an English sentence for testing language detection.",
        "これは日本語の  ストです。",
        "이것은 한국어 테스트입니다.",
        "Это предложение на русском языке.",
        "هذه جملة باللغة العربية.",
        "Dies ist ein deutscher Satz.",
        "C'est une phrase en français."
    ]
    
    for text in test_texts:
        try:
            detection = doubao_translator.doubao_detect_enhanced(text)
            print(f"Text: {text[:30]}...")
            print(f"Detection result: {detection}")
            print()
        except Exception as e:
            print(f"Error detecting language for '{text[:30]}...': {str(e)}")
            print()

    # 术语表测试
    print("\n----- 术语表测试 -----")
    
    # 创建示例术语表
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
    
    # 存术语表
    with open('glossary.json', 'w', encoding='utf-8') as f:
        json.dump(glossary_data, f, ensure_ascii=False, indent=2)
    
    # 创建带术语表的翻译器
    translator_with_glossary = DoubaoTranslator(
        api_key=api_key,  # 使用环境变量中的API密钥
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        glossary_path='glossary.json'
    )
    
    # 测试术语表翻译
    test_texts = [
        "人工智能和机器学习是现代科技的重要领域。",
        "Artificial Intelligence and Machine Learning are important fields in modern technology."
    ]
    
    for text in test_texts:
        # 检测语言
        detected = translator_with_glossary.doubao_detect(text)
        src = detected.lang
        dest = 'en' if src == 'zh' else 'zh'
        
        # 使用术语表翻译
        result = translator_with_glossary.apply_glossary(text, src=src, dest=dest)
        print(f"\nSource ({src}): {text}")
        print(f"Translation ({dest}): {result.text}")

    # 上下文感知翻译测试
    print("\n----- 上下文感知翻译测试 -----")
    
    # 测试场景1：歧义词翻译
    context1 = "这篇文章讨论了苹果公司的发展历程。"
    text1 = "苹果推出了革��性的产品。"
    
    result = translator_with_glossary.translate_with_context(
        text=text1,
        context=context1,
        dest='en'
    )
    print(f"\nContext: {context1}")
    print(f"Text: {text1}")
    print(f"Translation: {result.text}")

    # 测试场景2：专业文档翻译
    context2 = "在机器学习领域，神经网络是一个重要的研究方向。"
    text2 = "该网络的性能表现优异。"
    
    result = translator_with_glossary.translate_with_context(
        text=text2,
        context=context2,
        dest='en',
        style_guide="使用学术论文的式语气"
    )
    print(f"\nContext: {context2}")
    print(f"Text: {text2}")
    print(f"Translation: {result.text}")

    # 测试场景3：多段落文档翻译
    print("\n----- 文档翻译测试 -----")
    document = [
        "人工智能正在改变我们的生活。",
        "机器学习是其中最重要的分支。",
        "深度学习更是取得了突破性进展。",
        "这些技术正在各个领域得到应用。"
    ]
    
    results = translator_with_glossary.translate_document_with_context(
        paragraphs=document,
        dest='en',
        context_window=1
    )
    
    print("\nDocument Translation Results:")
    for i, result in enumerate(results, 1):
        print(f"\nParagraph {i}:")
        print(f"Original: {result.origin}")
        print(f"Translation: {result.text}")

    # 风格化翻译测试
    print("\n----- 风格化翻译测试 -----")
    
    # 测试预定义风格
    text = "人工智能正在改变我们的生活方式。"
    styles = ['formal', 'casual', 'technical', 'creative']
    
    for style in styles:
        result = translator_with_glossary.translate_with_style(
            text=text,
            dest='en',
            style=style
        )
        print(f"\nStyle: {style}")
        print(f"Original: {text}")
        print(f"Translation: {result.text}")

    # 测试自定义风格
    custom_style = {
        "语气": "幽默诙谐",
        "表达方式": "生动形象",
        "专业程度": "通俗易懂",
        "特殊要求": "可以适当添加有趣的比喻"
    }
    
    result = translator_with_glossary.translate_with_style(
        text=text,
        dest='en',
        style=custom_style
    )
    print(f"\nStyle: Custom")
    print(f"Original: {text}")
    print(f"Translation: {result.text}")

    # 测试带上下文的风格化翻译
    context = "这是一篇关于技术发展对社会影响的报告。"
    result = translator_with_glossary.translate_with_style(
        text=text,
        dest='en',
        style='technical',
        context=context
    )
    print(f"\nStyle: Technical with Context")
    print(f"Context: {context}")
    print(f"Original: {text}")
    print(f"Translation: {result.text}")

