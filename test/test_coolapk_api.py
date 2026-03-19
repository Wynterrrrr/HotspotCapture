import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get
from bs4 import BeautifulSoup
import json

def test_coolapk_api():
    """测试酷安API"""
    print("正在测试酷安API...")
    
    url = "https://api.coolapk.com/v6/main/indexV8?page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        print("❌ 请求失败")
        return
    
    print(f"响应状态码: {response.status_code}")
    
    try:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
    except:
        print(f"响应文本: {response.text[:500]}")

if __name__ == "__main__":
    test_coolapk_api()
