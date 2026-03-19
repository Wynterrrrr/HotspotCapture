import asyncio
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_51cto():
    try:
        spec = importlib.util.spec_from_file_location("_51cto", "c:\\Users\\zhang\\WorkSpace\\github\\PyDailyHotApi\\routes\\51cto.py")
        _51cto_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_51cto_module)
        
        result = await _51cto_module.get_51cto_hot()
        print("51CTO测试成功！")
        print(f"标题: {result.get('title')}")
        print(f"类型: {result.get('type')}")
        print(f"总数: {result.get('total')}")
        print(f"URL: {result.get('url')}")
        print(f"数据条数: {len(result.get('data', []))}")
        print(f"\n前5条数据:")
        for i, item in enumerate(result.get('data', [])[:5], 1):
            print(f"{i}. {item.get('title')}")
            print(f"   描述: {item.get('desc', '')}")
            print(f"   封面: {item.get('cover', '')}")
            print(f"   URL: {item.get('url')}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_51cto())
    sys.exit(0 if success else 1)
