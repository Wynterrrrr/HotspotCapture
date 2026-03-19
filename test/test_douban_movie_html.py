import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.http import get

async def test_douban_movie_html():
    try:
        url = "https://movie.douban.com/chart/"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        }
        
        response = get(url, headers=headers)
        if response:
            print("获取成功！")
            print(f"状态码: {response.status_code}")
            print(f"内容长度: {len(response.text)}")
            print(f"\n前1000个字符:\n{response.text[:1000]}")
            print(f"\n\n查找 .article tr.item:")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".article tr.item")
            print(f"找到 {len(items)} 个元素")
            
            if items:
                print(f"\n\n第一个元素的 HTML:\n{items[0].prettify()[:2000]}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_douban_movie_html())
    sys.exit(0 if success else 1)
