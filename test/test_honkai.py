import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.honkai import get_honkai_hot

async def test_honkai():
    """测试崩坏3最新动态接口"""
    print("正在测试崩坏3最新动态接口（公告）...")
    
    try:
        result = await get_honkai_hot(type="1")
        
        print(f"名称: {result['name']}")
        print(f"标题: {result['title']}")
        print(f"类型: {result['type']}")
        print(f"总数: {result['total']}")
        print(f"链接: {result['link']}")
        print(f"参数: {result.get('params', {})}")
        
        if result['data']:
            print("\n前5条数据:")
            for i, item in enumerate(result['data'][:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   描述: {item['desc'][:50] if item['desc'] else '无'}...")
                print(f"   封面: {item['cover'][:50] if item['cover'] else '无'}...")
                print(f"   时间: {item['timestamp']}")
                print(f"   热度: {item['hot']}")
                print(f"   URL: {item['url'][:50] if item['url'] else '无'}...")
        
        print("\n✅ 公告测试成功！")
    except Exception as e:
        print(f"\n❌ 公告测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试崩坏3最新动态接口（活动）...")
    
    try:
        result = await get_honkai_hot(type="2")
        
        print(f"名称: {result['name']}")
        print(f"标题: {result['title']}")
        print(f"类型: {result['type']}")
        print(f"总数: {result['total']}")
        
        if result['data']:
            print("\n前5条数据:")
            for i, item in enumerate(result['data'][:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   描述: {item['desc'][:50] if item['desc'] else '无'}...")
                print(f"   时间: {item['timestamp']}")
                print(f"   URL: {item['url'][:50] if item['url'] else '无'}...")
        
        print("\n✅ 活动测试成功！")
    except Exception as e:
        print(f"\n❌ 活动测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试崩坏3最新动态接口（资讯）...")
    
    try:
        result = await get_honkai_hot(type="3")
        
        print(f"名称: {result['name']}")
        print(f"标题: {result['title']}")
        print(f"类型: {result['type']}")
        print(f"总数: {result['total']}")
        
        if result['data']:
            print("\n前5条数据:")
            for i, item in enumerate(result['data'][:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   作者: {item['author']}")
                print(f"   描述: {item['desc'][:50] if item['desc'] else '无'}...")
                print(f"   时间: {item['timestamp']}")
                print(f"   URL: {item['url'][:50] if item['url'] else '无'}...")
        
        print("\n✅ 资讯测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 资讯测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_honkai())
    sys.exit(0 if success else 1)
