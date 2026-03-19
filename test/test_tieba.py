import requests
import json

url = "http://localhost:8000/tieba"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n标题: {data.get('title')}")
        print(f"类型: {data.get('type')}")
        print(f"描述: {data.get('description')}")
        print(f"链接: {data.get('link')}")
        print(f"总数: {data.get('total')}")
        print(f"\n前5条数据:")
        
        for i, item in enumerate(data.get('data', [])[:5], 1):
            print(f"\n{i}. {item.get('title')}")
            print(f"   ID: {item.get('id')}")
            print(f"   描述: {item.get('desc', 'N/A')}")
            print(f"   封面: {item.get('cover', 'N/A')}")
            print(f"   热度: {item.get('hot', 'N/A')}")
            print(f"   时间: {item.get('timestamp', 'N/A')}")
            print(f"   链接: {item.get('url', 'N/A')}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")