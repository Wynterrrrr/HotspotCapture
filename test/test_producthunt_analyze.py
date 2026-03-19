import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.producthunt.com"

scraper = cloudscraper.create_scraper()

try:
    response = scraper.get(url, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.text)}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有包含data-test属性的元素
        all_with_data_test = soup.find_all(attrs={"data-test": True})
        print(f"\n找到 {len(all_with_data_test)} 个包含data-test属性的元素")
        
        # 打印前20个data-test属性
        print("\n前20个data-test属性:")
        for i, elem in enumerate(all_with_data_test[:20], 1):
            data_test = elem.get("data-test", "")
            tag_name = elem.name
            print(f"{i}. <{tag_name}> data-test={data_test}")
        
        # 查找所有包含"post"的data-test属性
        post_divs = [div for div in all_with_data_test if "post" in div.get("data-test", "").lower()]
        print(f"\n找到 {len(post_divs)} 个包含'post'的data-test属性")
        
        if post_divs:
            print("\n前10个包含'post'的元素:")
            for i, div in enumerate(post_divs[:10], 1):
                data_test = div.get("data-test", "")
                print(f"{i}. data-test: {data_test}")
                
                # 尝试提取标题
                title_elem = div.find(attrs={"data-test": lambda x: x and "name" in x.lower()})
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    print(f"   标题: {title}")
                
                # 尝试提取链接
                link_elem = div.find("a")
                if link_elem:
                    href = link_elem.get("href", "")
                    print(f"   链接: {href}")
        
        # 查找所有script标签，看看是否有JSON数据
        scripts = soup.find_all("script")
        print(f"\n找到 {len(scripts)} 个script标签")
        
        # 查找包含"__NEXT_DATA__"或类似数据的script
        for script in scripts:
            script_content = script.string
            if script_content and ("__NEXT_DATA__" in script_content or "__INITIAL_STATE__" in script_content or "window.__STATE__" in script_content):
                print(f"\n找到包含数据的script标签:")
                print(f"内容长度: {len(script_content)}")
                print(f"前500字符: {script_content[:500]}...")
                break
        
        # 尝试查找所有a标签，看看是否有产品链接
        all_links = soup.find_all("a", href=True)
        print(f"\n找到 {len(all_links)} 个a标签")
        
        # 查找包含"/posts/"的链接
        post_links = [a for a in all_links if "/posts/" in a.get("href", "")]
        print(f"找到 {len(post_links)} 个包含'/posts/'的链接")
        
        if post_links:
            print("\n前10个产品链接:")
            for i, link in enumerate(post_links[:10], 1):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                print(f"{i}. {text[:50] if text else '无标题'}")
                print(f"   {href}")
                
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()
