import requests
import json

BASE_URL = "http://localhost:8000"

def test_weread():
    """测试微信读书热门榜单"""
    print("测试微信读书热门榜单...")
    
    try:
        response = requests.get(f"{BASE_URL}/weread", timeout=10)
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
                print(f"  作者: {first_item.get('author')}")
                print(f"  简介: {first_item.get('desc')}")
                print(f"  封面: {first_item.get('cover')}")
                print(f"  时间: {first_item.get('timestamp')}")
                print(f"  热度: {first_item.get('hot')}")
                print(f"  URL: {first_item.get('url')}")
                print(f"  移动端URL: {first_item.get('mobileUrl')}")
                
                print("\n测试成功！")
            else:
                print("警告: 没有返回数据")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_weread_with_type():
    """测试不同类型的微信读书榜单"""
    print("\n测试不同类型的微信读书榜单...")
    
    types = {
        "rising": "飙升榜",
        "hot_search": "热搜榜",
        "newbook": "新书榜",
        "general_novel_rising": "小说榜",
        "all": "总榜"
    }
    
    for type_id, type_name in types.items():
        try:
            response = requests.get(f"{BASE_URL}/weread?type={type_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"{type_name} (type={type_id}): {data.get('total')} 条数据")
            else:
                print(f"{type_name} (type={type_id}): 请求失败 - {response.status_code}")
        except Exception as e:
            print(f"{type_name} (type={type_id}): {str(e)}")

if __name__ == "__main__":
    test_weread()
    test_weread_with_type()
