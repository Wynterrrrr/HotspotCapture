import requests
import json

url = "http://localhost:8000/api/tieba"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n完整响应结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")