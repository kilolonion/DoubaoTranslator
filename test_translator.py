import asyncio
from doubaotrans import DoubaoTranslator

async def test_basic_translation():
    """测试基本翻译功能"""
    print("开始测试基本翻译功能...")
    async with DoubaoTranslator() as translator:
        # 英译中
        result = await translator.doubao_translate('Hello, World!', dest='zh')
        print(f'英译中结果: {result.text}')
        
        # 中译英
        result = await translator.doubao_translate('你好，世界！', dest='en')
        print(f'中译英结果: {result.text}')

async def test_streaming_translation():
    """测试流式翻译功能"""
    print("\n开始测试流式翻译功能...")
    async with DoubaoTranslator() as translator:
        async for result in await translator.doubao_translate('你好，这是一个测试。', dest='en', stream=True):
            print(f'流式翻译部分结果: {result.text}')

async def test_language_detection():
    """测试语言检测功能"""
    print("\n开始测试语言检测功能...")
    async with DoubaoTranslator() as translator:
        result = await translator.doubao_detect('这是中文测试')
        print(f'语言检测结果: {result}')

async def main():
    """运行所有测试"""
    try:
        await test_basic_translation()
        await test_streaming_translation()
        await test_language_detection()
        print("\n所有测试完成！")
    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 