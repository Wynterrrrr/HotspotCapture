import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.http import get
import xml.etree.ElementTree as ET

def test_coolapk_rss():
    """测试酷安RSS"""
    print("正在测试酷安RSS...")
    
    url = "https://www.coolapk.com/rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        print("❌ 请求失败")
        return
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)}")
    
    print("\n前500个字符:")
    print(response.text[:500])
    
    try:
        root = ET.fromstring(response.text)
        items = root.findall(".//item")
        print(f"\n找到 {len(items)} 个item")
        
        for i, item in enumerate(items[:3]):
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            
            print(f"\n{i+1}. {title.text if title is not None else '无标题'}")
            print(f"   链接: {link.text if link is not None else '无链接'}")
            print(f"   描述: {description.text[:100] if description is not None else '无描述'}...")
    except Exception as e:
        print(f"\n解析失败: {e}")

if __name__ == "__main__":
    test_coolapk_rss()
