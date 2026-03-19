import asyncio
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_52pojie():
    try:
        spec = importlib.util.spec_from_file_location("_52pojie", "c:\\Users\\zhang\\WorkSpace\\github\\PyDailyHotApi\\routes\\52pojie.py")
        _52pojie_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_52pojie_module)
        
        result = await _52pojie_module.get_52pojie_hot(type="digest")
        print("吾爱破解测试成功！")
        print(f"标题: {result.get('title')}")
        print(f"类型: {result.get('type')}")
        print(f"总数: {result.get('total')}")
        print(f"URL: {result.get('url')}")
        print(f"数据条数: {len(result.get('data', []))}")
        print(f"\n前5条数据:")
        for i, item in enumerate(result.get('data', [])[:5], 1):
            print(f"{i}. {item.get('title')}")
            print(f"   作者: {item.get('author', '')}")
            print(f"   描述: {item.get('desc', '')[:100]}...")
            print(f"   URL: {item.get('url')}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_52pojie())
    sys.exit(0 if success else 1)
