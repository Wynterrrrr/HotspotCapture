import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.douban_group import get_douban_group_hot

async def test_douban_group():
    try:
        result = await get_douban_group_hot()
        print("豆瓣讨论小组讨论精选测试成功！")
        print(f"标题: {result.get('title')}")
        print(f"类型: {result.get('type')}")
        print(f"总数: {result.get('total')}")
        print(f"URL: {result.get('url')}")
        print(f"数据条数: {len(result.get('data', []))}")
        if result.get('data'):
            print("\n前3条数据:")
            for i, item in enumerate(result['data'][:3], 1):
                print(f"{i}. {item.get('title')}")
                print(f"   描述: {item.get('desc', '')[:50]}...")
                print(f"   时间戳: {item.get('timestamp')}")
                print(f"   URL: {item.get('url')}")
                print(f"   移动端URL: {item.get('mobileUrl')}")
        return True
    except Exception as e:
        print(f"豆瓣讨论小组讨论精选测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_douban_group())
    sys.exit(0 if success else 1)
