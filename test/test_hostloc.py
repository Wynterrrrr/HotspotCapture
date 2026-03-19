import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.hostloc import get_hostloc_hot

async def test_hostloc():
    """测试全球主机交流榜单接口"""
    print("正在测试全球主机交流榜单接口（最新热门）...")
    
    try:
        result = await get_hostloc_hot(type="hot")
        
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
                print(f"   时间: {item['timestamp']}")
                print(f"   URL: {item['url'][:50] if item['url'] else '无'}...")
        
        print("\n✅ 最新热门测试成功！")
    except Exception as e:
        print(f"\n❌ 最新热门测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试全球主机交流榜单接口（最新精华）...")
    
    try:
        result = await get_hostloc_hot(type="digest")
        
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
        
        print("\n✅ 最新精华测试成功！")
    except Exception as e:
        print(f"\n❌ 最新精华测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试全球主机交流榜单接口（最新回复）...")
    
    try:
        result = await get_hostloc_hot(type="new")
        
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
        
        print("\n✅ 最新回复测试成功！")
    except Exception as e:
        print(f"\n❌ 最新回复测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试全球主机交流榜单接口（最新发表）...")
    
    try:
        result = await get_hostloc_hot(type="newthread")
        
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
        
        print("\n✅ 最新发表测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 最新发表测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hostloc())
    sys.exit(0 if success else 1)
