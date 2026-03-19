import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.lol import get_lol_hot

async def test_lol():
    """测试英雄联盟更新公告接口"""
    print("正在测试英雄联盟更新公告接口...")
    
    try:
        result = await get_lol_hot()
        
        print(f"名称: {result['name']}")
        print(f"标题: {result['title']}")
        print(f"类型: {result['type']}")
        print(f"总数: {result['total']}")
        print(f"链接: {result['link']}")
        
        if result['data']:
            print("\n前5条数据:")
            for i, item in enumerate(result['data'][:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   封面: {item['cover'][:50] if item['cover'] else '无'}...")
                print(f"   热度: {item['hot']}")
                print(f"   时间: {item['timestamp']}")
                print(f"   URL: {item['url'][:50] if item['url'] else '无'}...")
                print(f"   移动端URL: {item['mobileUrl'][:50] if item['mobileUrl'] else '无'}...")
        
        print("\n✅ 测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_lol())
    sys.exit(0 if success else 1)
