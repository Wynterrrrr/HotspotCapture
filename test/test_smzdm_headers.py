import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get

def test_smzdm_with_headers():
    """测试什么值得买API响应（带更多请求头）"""
    print("正在测试什么值得买API响应（带更多请求头）...")
    
    url = "https://post.smzdm.com/rank/json_more/?unit=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.smzdm.com/top/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    
    response = get(url, headers=headers)
    if not response:
        print("❌ 请求失败")
        return
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)}")
    print(f"Content-Type: {response.headers.get('Content-Type', '未知')}")
    
    print("\n前500个字符:")
    print(response.text[:500])
    
    print("\n\n尝试解析JSON...")
    try:
        data = response.json()
        print(f"✅ JSON解析成功")
        print(f"数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        if isinstance(data, dict) and 'data' in data:
            print(f"数据条数: {len(data.get('data', []))}")
    except Exception as e:
        print(f"❌ JSON解析失败: {e}")

if __name__ == "__main__":
    test_smzdm_with_headers()
