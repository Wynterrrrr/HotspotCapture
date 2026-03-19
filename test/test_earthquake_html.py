import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.http import get

async def test_earthquake_html():
    try:
        url = "https://news.ceic.ac.cn/speedsearch.html"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = get(url, headers=headers)
        if response:
            print("获取成功！")
            print(f"状态码: {response.status_code}")
            print(f"内容长度: {len(response.text)}")
            print(f"\n前2000个字符:\n{response.text[:2000]}")
            print(f"\n\n查找 const newdata:")
            import re
            regex = r"const newdata = (\[.*?\]);"
            match = re.search(regex, response.text, re.DOTALL)
            if match:
                print(f"找到匹配: {match.group(1)[:500]}...")
            else:
                print("未找到匹配")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_earthquake_html())
    sys.exit(0 if success else 1)
