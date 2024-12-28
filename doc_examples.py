from doubaotrans import DoubaoTranslator, DoubaoTranslated, DoubaoDetected
import json
import time
import asyncio
from typing import Dict, Any

class DocumentationExamples:
    def __init__(self):
        self.examples = {}
        self.translator = None
    
    async def run_all_examples(self):
        """运行所有示例并收集结果"""
        try:
            # 1. 初始化示例
            print("\n=== 初始化示例 ===")
            self.examples['initialization'] = await self.initialization_examples()
            
            # 2. 基础翻译示例
            print("\n=== 基础翻译示例 ===")
            self.examples['basic_translation'] = await self.basic_translation_examples()
            
            # 3. 流式翻译示例
            print("\n=== 流式翻译示例 ===")
            self.examples['stream_translation'] = await self.stream_translation_examples()
            
            # 4. 批量翻译示例
            print("\n=== 批量翻译示例 ===")
            self.examples['batch_translation'] = await self.batch_translation_examples()
            
            # 5. 语言检���示例
            print("\n=== 语言检测示例 ===")
            self.examples['language_detection'] = await self.language_detection_examples()
            
            # 6. 术语表示例
            print("\n=== 术语表示例 ===")
            self.examples['glossary'] = await self.glossary_examples()
            
            # 7. 上下文翻译示例
            print("\n=== 上下文翻译示例 ===")
            self.examples['context_translation'] = await self.context_translation_examples()
            
            # 8. 风格化翻译示例
            print("\n=== 风格化翻译示例 ===")
            self.examples['style_translation'] = await self.style_translation_examples()
            
            # 9. 性能配置示例
            print("\n=== 性能配置示例 ===")
            self.examples['performance'] = await self.performance_examples()
            
            # 10. 错误处理示例
            print("\n=== 错误处理示例 ===")
            self.examples['error_handling'] = await self.error_handling_examples()
            
            # 导出结果
            self.export_results()
            
        except Exception as e:
            print(f"Error running examples: {str(e)}")
    
    async def initialization_examples(self) -> Dict[str, Any]:
        """初始���示例"""
        results = {}
        
        # 基本初始化
        translator = DoubaoTranslator()
        results['basic'] = translator.get_config()
        
        # 不同性能模式
        for mode in ['fast', 'balanced', 'accurate']:
            translator = DoubaoTranslator(performance_mode=mode)
            results[f'mode_{mode}'] = translator.get_config()
        
        # 自定义配置
        translator = DoubaoTranslator(
            performance_mode='balanced',
            max_workers=4,
            cache_ttl=3600,
            max_tokens=200
        )
        results['custom'] = translator.get_config()
        
        self.translator = translator
        return results
    
    async def basic_translation_examples(self) -> Dict[str, Any]:
        """基础翻译示例"""
        results = {}
        
        # 基本用法
        results['simple'] = {
            'zh_to_en': str(self.translator.doubao_translate("你好世界", dest='en')),
            'en_to_zh': str(self.translator.doubao_translate("Hello, world!", dest='zh'))
        }
        
        # 指定源语言
        results['specified_source'] = str(self.translator.doubao_translate(
            "Hello, world!", src='en', dest='zh'
        ))
        
        # 多语言示例
        test_texts = {
            'zh': "这是中文",
            'en': "This is English",
            'ja': "これは日本語です",
            'ko': "이것은 한국어입니다",
            'fr': "C'est le français",
            'de': "Das ist Deutsch"
        }
        
        results['multilingual'] = {
            lang: str(self.translator.doubao_translate(text, dest='en'))
            for lang, text in test_texts.items()
        }
        
        return results
    
    async def stream_translation_examples(self) -> Dict[str, Any]:
        """流式翻译示例"""
        results = {}
        
        # 基本流式翻译
        result = self.translator.doubao_translate("你好世界", dest='en', stream=True)
        results['basic_stream'] = str(result)
        
        # 长文本流式翻译
        long_text = "这是一个很长的文本。" * 5
        result = self.translator.doubao_translate(long_text, dest='en', stream=True)
        results['long_text_stream'] = str(result)
        
        return results
    
    async def batch_translation_examples(self) -> Dict[str, Any]:
        """批量翻译示例"""
        results = {}
        
        # 简单批量
        texts = ["你好", "世界", "人工智能"]
        results['simple_batch'] = [
            str(result) for result in self.translator.doubao_translate(texts, dest='en')
        ]
        
        # 大批量
        large_texts = [f"文本{i}" for i in range(10)]
        results['large_batch'] = [
            str(result) for result in self.translator.doubao_translate(large_texts, dest='en')
        ]
        
        # 异步批量
        async_results = await self.translator.translate_batch_async(texts, dest='en')
        results['async_batch'] = [str(result) for result in async_results]
        
        return results
    
    async def language_detection_examples(self) -> Dict[str, Any]:
        """语言检测示例"""
        results = {}
        
        # 基本检测
        test_texts = {
            'zh': "这是中文文本",
            'en': "This is English text",
            'ja': "これは日本語のテキストです",
            'ko': "이것은 한국어 텍스트입니다",
            'mixed': "这是 Mixed 文本 with English"
        }
        
        results['basic_detection'] = {
            lang: str(self.translator.doubao_detect(text))
            for lang, text in test_texts.items()
        }
        
        # 增强检测
        results['enhanced_detection'] = {
            lang: str(self.translator.doubao_detect_enhanced(text))
            for lang, text in test_texts.items()
        }
        
        return results
    
    async def glossary_examples(self) -> Dict[str, Any]:
        """术语表示例"""
        results = {}
        
        # 创建术语表
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
            },
            "NLP": {
                "en": "Natural Language Processing",
                "zh": "自然语言处理",
                "ja": "自然言語処理"
            }
        }
        
        # 保存术语表
        with open('test_glossary.json', 'w', encoding='utf-8') as f:
            json.dump(glossary_data, f, ensure_ascii=False, indent=2)
        
        # 使用术语表
        translator_with_glossary = DoubaoTranslator(glossary_path='test_glossary.json')
        
        test_texts = {
            'zh_to_en': "AI和ML在NLP领域发挥重要作用",
            'en_to_zh': "AI and ML are important in NLP",
            'ja_to_en': "AIとMLはNLPで重要です"
        }
        
        results['with_glossary'] = {
            key: str(translator_with_glossary.apply_glossary(text, src='auto', dest='en'))
            for key, text in test_texts.items()
        }
        
        return results
    
    async def context_translation_examples(self) -> Dict[str, Any]:
        """上下文翻译示例"""
        results = {}
        
        # 歧义词翻译
        contexts = {
            'apple_company': {
                'context': "这篇文章讨论了苹果公司的发展历程。",
                'text': "苹果发布了新产品。"
            },
            'apple_fruit': {
                'context': "这篇文章讨论了水果的营养价值。",
                'text': "苹果富含维生素。"
            }
        }
        
        results['disambiguation'] = {
            key: str(self.translator.translate_with_context(
                text=data['text'],
                context=data['context'],
                dest='en'
            ))
            for key, data in contexts.items()
        }
        
        # 文档翻译
        document = [
            "人工智能正在改变我们的生活。",
            "机器学习是其中最重要的分支。",
            "深度学习更是取得了突破性进展。"
        ]
        
        results['document'] = [
            str(result) for result in self.translator.translate_document_with_context(
                paragraphs=document,
                dest='en',
                context_window=1
            )
        ]
        
        return results
    
    async def style_translation_examples(self) -> Dict[str, Any]:
        """风格化翻译示例"""
        results = {}
        
        text = "人工智能正在改变我们的生活方式"
        
        # 预定义风格
        results['predefined_styles'] = {
            style: str(self.translator.translate_with_style(text, style=style, dest='en'))
            for style in ['formal', 'casual', 'technical', 'creative']
        }
        
        # 自定义风格
        custom_styles = {
            'humorous': {
                "语气": "幽默诙谐",
                "表达方式": "生动形象",
                "专业程度": "通俗易懂"
            },
            'academic': {
                "语气": "严谨学术",
                "表达方式": "规范专业",
                "专业程度": "高度专业"
            }
        }
        
        results['custom_styles'] = {
            style_name: str(self.translator.translate_with_style(
                text, style=style_config, dest='en'
            ))
            for style_name, style_config in custom_styles.items()
        }
        
        return results
    
    async def performance_examples(self) -> Dict[str, Any]:
        """性能配置示例"""
        results = {}
        
        # 不同性能模式
        for mode in ['fast', 'balanced', 'accurate']:
            translator = DoubaoTranslator(performance_mode=mode)
            start_time = time.time()
            result = translator.doubao_translate("测试文本", dest='en')
            duration = time.time() - start_time
            
            results[f'mode_{mode}'] = {
                'config': translator.get_config(),
                'duration': duration,
                'result': str(result)
            }
        
        # 自定义性能配置
        self.translator.set_performance_config(
            max_tokens=300,
            temperature=0.4,
            timeout=20,
            cache_ttl=3600
        )
        results['custom_config'] = self.translator.get_config()
        
        return results
    
    async def error_handling_examples(self) -> Dict[str, Any]:
        """错误处理示例"""
        results = {}
        
        # 测试各种错误情况
        error_cases = {
            'empty_text': "",
            'invalid_lang': ("Hello", "invalid_lang"),
            'long_text': "a" * 5000,
            'invalid_api_key': "invalid_key"
        }
        
        for case_name, test_data in error_cases.items():
            try:
                if isinstance(test_data, tuple):
                    self.translator.doubao_translate(test_data[0], dest=test_data[1])
                else:
                    self.translator.doubao_translate(test_data, dest='en')
            except Exception as e:
                results[case_name] = {
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
        
        return results
    
    def export_results(self):
        """导出测试结果"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'doc_examples_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.examples, f, ensure_ascii=False, indent=2)
        print(f"\n结果已导出到: {filename}")

if __name__ == "__main__":
    examples = DocumentationExamples()
    asyncio.run(examples.run_all_examples()) 