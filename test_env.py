import asyncio
from doubaotrans import DoubaoTranslator
import os
from dotenv import load_dotenv

async def test_env_config():
    """测试.env配置加载"""
    # 确保加载.env文件
    load_dotenv()
    
    # 打印环境变量
    print("环境变量检查:")
    print(f"DOUBAO_API_KEY: {'已设置' if os.getenv('DOUBAO_API_KEY') else '未设置'}")
    print(f"DOUBAO_MODEL: {os.getenv('DOUBAO_MODEL', '未设置')}")
    print(f"DOUBAO_PERFORMANCE_MODE: {os.getenv('DOUBAO_PERFORMANCE_MODE', '未设置')}")
    print(f"DOUBAO_BASE_URL: {os.getenv('DOUBAO_BASE_URL', '未设置')}")
    
    try:
        # 创建翻译器实例
        async with DoubaoTranslator() as translator:
            # 测试配置获取
            config = translator.get_config()
            print("\n翻译器配置:")
            print(f"模型: {config.get('model_name')}")
            print(f"性能模式: {config.get('performance_mode')}")
            print(f"基础URL: {config.get('base_url')}")
            
            # 测试连接
            is_connected = await translator.test_connection()
            print(f"\n连接测试: {'成功' if is_connected else '失败'}")
            
            if is_connected:
                # 测试翻译
                result = await translator.doubao_translate("Hello world", dest="zh")
                print(f"\n翻译测试: {result.text}")
                
    except Exception as e:
        print(f"\n错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_env_config()) 