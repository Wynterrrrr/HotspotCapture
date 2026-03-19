import requests
import json

BASE_URL = "http://localhost:8000"

def test_sina_news():
    """测试新浪新闻热点榜"""
    print("测试新浪新闻热点榜...")
    
    try:
        response = requests.get(f"{BASE_URL}/sina-news", timeout=10)
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

def test_sina_news_with_type():
    """测试不同分类的新浪新闻"""
    print("\n测试不同分类的新浪新闻...")
    
    types = {
        "1": "总排行",
        "4": "国内新闻",
        "5": "国际新闻",
        "7": "体育新闻",
        "8": "财经新闻",
        "9": "娱乐新闻",
        "10": "科技新闻"
    }
    
    for type_id, type_name in types.items():
        try:
            response = requests.get(f"{BASE_URL}/sina-news?type={type_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"{type_name} (type={type_id}): {data.get('total')} 条数据")
            else:
                print(f"{type_name} (type={type_id}): 请求失败 - {response.status_code}")
        except Exception as e:
            print(f"{type_name} (type={type_id}): {str(e)}")

if __name__ == "__main__":
    test_sina_news()
    test_sina_news_with_type()
