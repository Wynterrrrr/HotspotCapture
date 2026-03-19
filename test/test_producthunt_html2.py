import requests
from bs4 import BeautifulSoup

url = "https://www.producthunt.com"

# 使用更真实的浏览器请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找post items
        post_items = soup.select("[data-test=homepage-section-0] [data-test^=post-item]")
        print(f"找到 {len(post_items)} 个post items")
        
        if len(post_items) > 0:
            print("\n前3条数据:")
            for i, item in enumerate(post_items[:3], 1):
                title_elem = item.select_one("a[data-test^=post-name]")
                title = title_elem.get_text(strip=True) if title_elem else "无标题"
                
                data_test = item.get("data-test", "")
                id_value = data_test.replace("post-item-", "") if data_test else "无ID"
                
                vote_elem = item.select_one("[data-test=vote-button]")
                vote_text = vote_elem.get_text(strip=True) if vote_elem else "0"
                
                print(f"\n{i}. {title}")
                print(f"   ID: {id_value}")
                print(f"   热度: {vote_text}")
        else:
            print("\n未找到post items，尝试查找其他选择器...")
            
            # 尝试查找其他可能的选择器
            all_divs = soup.find_all("div")
            print(f"总共有 {len(all_divs)} 个div元素")
            
            # 查找包含"post"的data-test属性
            post_divs = [div for div in all_divs if div.get("data-test", "").startswith("post")]
            print(f"找到 {len(post_divs)} 个包含'post'的data-test属性")
            
            if post_divs:
                print("\n前3个包含'post'的元素:")
                for i, div in enumerate(post_divs[:3], 1):
                    data_test = div.get("data-test", "")
                    print(f"{i}. data-test: {data_test}")
                    print(f"   HTML: {str(div)[:200]}...")
    else:
        print(f"\n请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()
