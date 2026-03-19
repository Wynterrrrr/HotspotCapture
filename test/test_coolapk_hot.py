import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get
from bs4 import BeautifulSoup

def test_coolapk_hot():
    """测试酷安热榜页面"""
    print("正在测试酷安热榜页面...")
    
    url = "https://www.coolapk.com/hot"
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
    
    print("\n前500个字符:")
    print(html[:500])
    
    print("\n搜索script标签...")
    scripts = soup.find_all('script')
    print(f"找到 {len(scripts)} 个script标签")
    
    for i, script in enumerate(scripts):
        if script.string and ('hot' in script.string.lower() or 'list' in script.string.lower()):
            print(f"\nScript {i} 包含 'hot' 或 'list':")
            print(script.string[:500])
    
    print("\n搜索div标签...")
    divs = soup.find_all('div')
    print(f"找到 {len(divs)} 个div标签")
    
    for i, div in enumerate(divs):
        class_name = str(div.get('class', ''))
        if 'hot' in class_name.lower() or 'list' in class_name.lower() or 'item' in class_name.lower():
            print(f"\nDiv {i} class包含 'hot', 'list' 或 'item':")
            print(f"Class: {div.get('class', '')}")
            print(f"Text: {div.get_text()[:200]}")

if __name__ == "__main__":
    test_coolapk_hot()
