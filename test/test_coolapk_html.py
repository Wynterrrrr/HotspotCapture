import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get

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
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应长度: {len(html)}")
    
    print("\n前500个字符:")
    print(html[:500])
    
    print("\n\n搜索__INITIAL_STATE__...")
    if "__INITIAL_STATE__" in html:
        print("✅ 找到__INITIAL_STATE__")
        start = html.find("__INITIAL_STATE__")
        print(f"位置: {start}")
        print(f"上下文: {html[start:start+200]}")
    else:
        print("❌ 未找到__INITIAL_STATE__")
    
    print("\n\n搜索window...")
    if "window" in html:
        print("✅ 找到window")
        count = html.count("window")
        print(f"出现次数: {count}")
    else:
        print("❌ 未找到window")

if __name__ == "__main__":
    test_coolapk_html()
