import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get
from bs4 import BeautifulSoup

def test_coolapk_html():
    """测试酷安HTML响应"""
    print("正在测试酷安HTML响应...")
    
    url = "https://www.coolapk.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        print("❌ 请求失败")
        return
    
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应长度: {len(html)}")
    
    print("\n搜索script标签...")
    scripts = soup.find_all('script')
    print(f"找到 {len(scripts)} 个script标签")
    
    for i, script in enumerate(scripts):
        if script.string and 'hot' in script.string.lower():
            print(f"\nScript {i} 包含 'hot':")
            print(script.string[:500])
    
    print("\n搜索div标签...")
    divs = soup.find_all('div')
    print(f"找到 {len(divs)} 个div标签")
    
    for i, div in enumerate(divs):
        if 'hot' in str(div.get('class', '')).lower() or 'hot' in div.get_text()[:100].lower():
            print(f"\nDiv {i} 包含 'hot':")
            print(f"Class: {div.get('class', '')}")
            print(f"Text: {div.get_text()[:200]}")

if __name__ == "__main__":
    test_coolapk_html()
