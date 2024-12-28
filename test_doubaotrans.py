from doubaotrans import DoubaoTranslator, DoubaoTranslated, DoubaoDetected
import os
from dotenv import load_dotenv
import json
import time
from typing import Dict, Any
import openai
import asyncio
from concurrent.futures import ThreadPoolExecutor
import statistics
import re

class TestMetrics:
    """测试指标收集类"""
    def __init__(self):
        self.response_times = []
        self.token_counts = []
        self.error_counts = {}
        self.quality_scores = []
        self.latency_distribution = []  # 添加延迟分布
        self.success_rates = {}  # 添加成功率统计
        self.memory_usage = []  # 添加内存使用统计
        
    def add_response_time(self, duration: float):
        self.response_times.append(duration)
        
    def add_token_count(self, count: int):
        self.token_counts.append(count)
        
    def add_error(self, error_type: str):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
    def add_quality_score(self, score: float):
        self.quality_scores.append(score)
        
    def add_latency(self, latency: float, category: str):
        self.latency_distribution.append((category, latency))
        
    def add_success(self, category: str, success: bool):
        if category not in self.success_rates:
            self.success_rates[category] = {'success': 0, 'total': 0}
        self.success_rates[category]['total'] += 1
        if success:
            self.success_rates[category]['success'] += 1
            
    def get_statistics(self) -> Dict[str, Any]:
        stats = {
            'response_times': {
                'average': statistics.mean(self.response_times) if self.response_times else 0,
                'min': min(self.response_times) if self.response_times else 0,
                'max': max(self.response_times) if self.response_times else 0,
                'median': statistics.median(self.response_times) if self.response_times else 0
            },
            'token_usage': {
                'average': statistics.mean(self.token_counts) if self.token_counts else 0,
                'total': sum(self.token_counts) if self.token_counts else 0
            },
            'error_rates': {
                error_type: count/len(self.response_times) if self.response_times else 0
                for error_type, count in self.error_counts.items()
            },
            'quality_scores': {
                'average': statistics.mean(self.quality_scores) if self.quality_scores else 0,
                'min': min(self.quality_scores) if self.quality_scores else 0,
                'max': max(self.quality_scores) if self.quality_scores else 0
            }
        }
        stats.update({
            'latency_distribution': {
                category: {
                    'avg': statistics.mean([l for c, l in self.latency_distribution if c == category]),
                    'p95': statistics.quantiles([l for c, l in self.latency_distribution if c == category], n=20)[18] if self.latency_distribution else 0,
                    'p99': statistics.quantiles([l for c, l in self.latency_distribution if c == category], n=100)[98] if self.latency_distribution else 0
                }
                for category in set(c for c, _ in self.latency_distribution)
            },
            'success_rates': {
                category: {
                    'rate': stats['success'] / stats['total'] if stats['total'] > 0 else 0,
                    'total': stats['total']
                }
                for category, stats in self.success_rates.items()
            }
        })
        return stats

def run_comprehensive_tests():
    """运行全面测试"""
    metrics = TestMetrics()
    results = []
    
    try:
        # 1. 初始化测试
        print("\n=== ���始化和配置测试 ===")
        start_time = time.time()
        
        # 测试不同性能模式
        for mode in ['fast', 'balanced', 'accurate']:
            try:
                translator = DoubaoTranslator(performance_mode=mode)
                config = translator.get_config()
                duration = time.time() - start_time
                results.append({
                    'test': f'初始化-{mode}模式',
                    'status': 'success',
                    'duration': duration,
                    'config': config
                })
                metrics.add_response_time(duration)
            except Exception as e:
                results.append({
                    'test': f'初始化-{mode}模式',
                    'status': 'failed',
                    'error': str(e)
                })
                metrics.add_error('initialization')

        # 2. 功能测试
        translator = DoubaoTranslator(performance_mode='balanced')
        
        # 2.1 基础翻译测试
        print("\n=== 基础翻译测试 ===")
        test_cases = [
            ("你好世界", "en", "auto", "中译英-简单"),
            ("人工智能正在改变世界", "en", "auto", "中译英-复杂"),
            ("Hello, world!", "zh", "en", "英译中-简单"),
            ("Artificial Intelligence is transforming the world", "zh", "en", "英译中-复杂"),
            ("こんにちは世界", "en", "auto", "日译英"),
            ("안녕하세요 세상", "en", "auto", "韩译英")
        ]
        
        for text, dest, src, case_name in test_cases:
            try:
                start = time.time()
                result = translator.doubao_translate(text, dest=dest, src=src)
                duration = time.time() - start
                
                # 使用改进的质量评分
                quality_score = calculate_quality_score(text, result.text)
                metrics.add_quality_score(quality_score)
                
                results.append({
                    'test': f'基础翻译-{case_name}',
                    'status': 'success',
                    'duration': duration,
                    'input': text,
                    'output': result.text,
                    'quality_score': quality_score,
                    'quality_details': {
                        'length_ratio': len(result.text) / len(text),
                        'has_punctuation': bool(re.search(r'[,.!?，。！？]', result.text)),
                        'preserves_format': bool(re.search(r'[A-Z0-9]', text)) == bool(re.search(r'[A-Z0-9]', result.text))
                    }
                })
                metrics.add_response_time(duration)
            except Exception as e:
                results.append({
                    'test': f'基础翻译-{case_name}',
                    'status': 'failed',
                    'error': str(e)
                })
                metrics.add_error('translation')

        # 2.2 并发性能测试
        print("\n=== 并发性能测试 ===")
        texts = ["文本" + str(i) for i in range(10)]
        start = time.time()
        batch_results = translator.translate_batch(texts, dest='en')
        duration = time.time() - start
        
        results.append({
            'test': '并发翻译',
            'status': 'success',
            'duration': duration,
            'average_time_per_text': duration / len(texts),
            'success_rate': len([r for r in batch_results if r.text]) / len(texts)
        })

        # 2.3 错误处理测试
        print("\n=== 错误处理测试 ===")
        error_cases = [
            ("", "en", "空文本"),
            ("a" * 5000, "en", "超长文本"),
            ("Hello", "invalid_lang", "无效语言"),
        ]
        
        for text, dest, case_name in error_cases:
            try:
                translator.doubao_translate(text, dest=dest)
                results.append({
                    'test': f'错误处理-{case_name}',
                    'status': 'failed',
                    'error': '未能捕获预期错误'
                })
            except Exception as e:
                results.append({
                    'test': f'错误处理-{case_name}',
                    'status': 'success',
                    'error_type': type(e).__name__
                })

        # 2.4 风格化翻译测试
        print("\n=== 风格化翻译测试 ===")
        text = "人工智能正在改变我们的生活"
        styles = ['formal', 'casual', 'technical', 'creative']
        
        for style in styles:
            try:
                start = time.time()
                result = translator.translate_with_style(text, style=style)
                duration = time.time() - start
                
                results.append({
                    'test': f'风格化翻译-{style}',
                    'status': 'success',
                    'duration': duration,
                    'input': text,
                    'output': result.text,
                    'style_adherence': 'style' in result.text.lower()
                })
                metrics.add_response_time(duration)
            except Exception as e:
                results.append({
                    'test': f'风格化翻译-{style}',
                    'status': 'failed',
                    'error': str(e)
                })
                metrics.add_error('style')

        # 2.5 长文本处理测试
        print("\n=== 长文本处理测试 ===")
        long_text = "这是一个很长的文本。" * 20
        try:
            start = time.time()
            result = translator.doubao_translate(long_text, dest='en')
            duration = time.time() - start
            
            results.append({
                'test': '长文本处理',
                'status': 'success',
                'duration': duration,
                'input_length': len(long_text),
                'output_length': len(result.text)
            })
            metrics.add_response_time(duration)
        except Exception as e:
            results.append({
                'test': '长文本处理',
                'status': 'failed',
                'error': str(e)
            })
            metrics.add_error('long_text')

        # 3. 性能测试
        print("\n=== 性能压力测试 ===")
        
        # 3.1 连续请求测试
        start = time.time()
        for i in range(5):
            try:
                translator.doubao_translate("测试文本" + str(i))
                time.sleep(0.1)  # 避免触发限���
            except Exception as e:
                metrics.add_error('continuous_requests')
        
        results.append({
            'test': '连续请求测试',
            'status': 'success',
            'duration': time.time() - start,
            'requests_per_second': 5 / (time.time() - start)
        })

    except Exception as e:
        results.append({
            'test': '整体测试',
            'status': 'failed',
            'error': str(e)
        })

    return results, metrics

def print_test_report(results: list, metrics: TestMetrics):
    """打印更详细的测试报告"""
    print("\n" + "="*50)
    print("详细测试报告")
    print("="*50)
    
    # 1. 执行摘要
    print("\n1. 执行摘要")
    stats = metrics.get_statistics()
    print(f"总测试数: {len(results)}")
    print(f"总执行时间: {stats['response_times']['max'] - stats['response_times']['min']:.2f}秒")
    print(f"平均响应时间: {stats['response_times']['average']:.3f}秒")
    
    # 2. 性能分析
    print("\n2. 性能分析")
    print("响应时间分布:")
    for category, latency in stats['latency_distribution'].items():
        print(f"  {category}:")
        print(f"    平均: {latency['avg']:.3f}秒")
        print(f"    P95: {latency['p95']:.3f}秒")
        print(f"    P99: {latency['p99']:.3f}秒")
    
    # 3. 质量评估
    print("\n3. 质量评估")
    print(f"平均质量分数: {stats['quality_scores']['average']:.2f}")
    print(f"最高质量分数: {stats['quality_scores']['max']:.2f}")
    print(f"最低质量分数: {stats['quality_scores']['min']:.2f}")
    
    # 4. 错误分析
    if stats['error_rates']:
        print("\n4. 错误分析")
        for error_type, rate in stats['error_rates'].items():
            print(f"{error_type}: {rate*100:.1f}%")
    
    # 5. 成功率分析
    print("\n5. 成功率分析")
    for category, stats in stats['success_rates'].items():
        print(f"{category}: {stats['rate']*100:.1f}% ({stats['total']} 测试)")

def calculate_quality_score(original: str, translated: str) -> float:
    """计算翻译质量分数"""
    # 基础分数
    base_score = 0.5
    
    # 长度比例评分 (0.0-0.3)
    length_ratio = len(translated) / len(original)
    if 0.5 <= length_ratio <= 2.0:
        length_score = 0.3 * (1 - abs(1 - length_ratio))
    else:
        length_score = 0
        
    # 标点符号一致性 (0.0-0.2)
    orig_puncts = set([c for c in original if not c.isalnum()])
    trans_puncts = set([c for c in translated if not c.isalnum()])
    punct_score = 0.2 * len(orig_puncts.intersection(trans_puncts)) / max(len(orig_puncts), 1)
    
    # 保留原文特殊标记的评分 (0.0-0.2)
    special_marks = re.findall(r'[A-Z0-9]+|["""]', original)
    preserved_marks = sum(1 for mark in special_marks if mark in translated)
    preservation_score = 0.2 * (preserved_marks / max(len(special_marks), 1))
    
    return base_score + length_score + punct_score + preservation_score

if __name__ == "__main__":
    results, metrics = run_comprehensive_tests()
    print_test_report(results, metrics) 