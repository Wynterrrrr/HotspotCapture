import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.weatheralarm import get_weatheralarm_hot

async def test_weatheralarm():
    try:
        result = await get_weatheralarm_hot()
        print("中央气象台测试成功！")
        print(f"标题: {result.get('title')}")
        print(f"类型: {result.get('type')}")
        print(f"总数: {result.get('total')}")
        print(f"URL: {result.get('url')}")
        print(f"数据条数: {len(result.get('data', []))}")
        print(f"\n前3条数据:")
        for i, item in enumerate(result.get('data', [])[:3], 1):
            print(f"{i}. {item.get('title')}")
            print(f"   描述: {item.get('desc', '')}")
            print(f"   封面: {item.get('cover', '')}")
            print(f"   时间戳: {item.get('timestamp')}")
            print(f"   URL: {item.get('url')}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_weatheralarm())
    sys.exit(0 if success else 1)
