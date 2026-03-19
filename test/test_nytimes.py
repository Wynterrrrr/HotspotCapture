import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.nytimes import get_nytimes_hot

async def test_nytimes():
    """测试纽约时报热点接口"""
    print("正在测试纽约时报热点接口（中文网）...")
    
    try:
        result = await get_nytimes_hot(area="china")
        
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
        
        print("\n✅ 中文网测试成功！")
    except Exception as e:
        print(f"\n❌ 中文网测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\n正在测试纽约时报热点接口（全球版）...")
    
    try:
        result = await get_nytimes_hot(area="global")
        
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
        
        print("\n✅ 全球版测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 全球版测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_nytimes())
    sys.exit(0 if success else 1)
