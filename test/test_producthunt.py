import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.producthunt import get_producthunt_hot

async def test_producthunt():
    """测试Product Hunt接口"""
    print("正在测试Product Hunt接口...")
    
    try:
        result = await get_producthunt_hot()
        
        print(f"名称: {result.get('name')}")
        print(f"标题: {result.get('title')}")
        print(f"类型: {result.get('type')}")
        print(f"描述: {result.get('description')}")
        print(f"总数: {result.get('total')}")
        print(f"链接: {result.get('link')}")
        
        if result.get('data'):
            print("\n前5条数据:")
            for i, item in enumerate(result['data'][:5], 1):
                print(f"\n{i}. {item.get('title')}")
                print(f"   ID: {item.get('id')}")
                print(f"   热度: {item.get('hot')}")
                print(f"   时间: {item.get('timestamp')}")
                print(f"   URL: {item.get('url')[:50] if item.get('url') else '无'}...")
                print(f"   移动URL: {item.get('mobileUrl')[:50] if item.get('mobileUrl') else '无'}...")
        
        print("\n✅ 测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_producthunt())
    sys.exit(0 if success else 1)
