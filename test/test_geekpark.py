import requests
import json

BASE_URL = "http://localhost:8000"

def test_geekpark():
    """测试极客公园热门文章"""
    print("测试极客公园热门文章...")
    
    try:
        response = requests.get(f"{BASE_URL}/geekpark", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"标题: {data.get('title')}")
            print(f"类型: {data.get('type')}")
            print(f"总数: {data.get('total')}")
            print(f"数据条数: {len(data.get('data', []))}")
            
            if data.get('data'):
                first_item = data['data'][0]
                print(f"\n第一条数据:")
                print(f"  标题: {first_item.get('title')}")
                print(f"  描述: {first_item.get('desc')[:100] if first_item.get('desc') else 'N/A'}...")
                print(f"  封面: {first_item.get('cover')}")
                print(f"  作者: {first_item.get('author')}")
                print(f"  热度: {first_item.get('hot')}")
                print(f"  时间: {first_item.get('timestamp')}")
                print(f"  URL: {first_item.get('url')}")
                print(f"  移动端URL: {first_item.get('mobileUrl')}")
                
                print("\n测试成功！")
            else:
                print("警告: 没有返回数据")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_geekpark()
