from fastapi import APIRouter
from utils.http import get
from utils.cache import cache
from config import config
from bs4 import BeautifulSoup

router = APIRouter()


@router.get("/cls")
async def get_cls_hot():
    """获取财联社热点"""
    cache_key = "cls"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    url = "https://www.cls.cn/telegraph"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        response = get(url, headers=headers, timeout=15)
        if not response:
            return {"data": [], "title": "财联社", "url": url, "total": 0}

        soup = BeautifulSoup(response.text, "html.parser")
        items = []

        # 尝试从页面获取数据
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "telegraph-list" in str(script.string):
                import json
                import re

                try:
                    # 尝试提取JSON数据
                    match = re.search(r'"list":\s*(\[.*?\])', script.string, re.DOTALL)
                    if match:
                        data_list = json.loads(match.group(1))
                        for item in data_list[:30]:
                            items.append(
                                {
                                    "id": item.get("id", ""),
                                    "title": item.get("title", item.get("content", "")),
                                    "content": item.get("content", ""),
                                    "hot": item.get("readCount", 0),
                                    "url": f"https://www.cls.cn/detail/{item.get('id', '')}",
                                    "type": "cls",
                                }
                            )
                        break
                except:
                    pass

        # 如果脚本提取失败，尝试页面解析
        if not items:
            telegraph_items = soup.select(
                ".telegraph-content li, .news-item, .list-item"
            )
            for item in telegraph_items[:30]:
                title_elem = item.select_one("a, .title, .content")
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get("href", "") if title_elem.name == "a" else ""

                    if title:
                        items.append(
                            {
                                "id": len(items) + 1,
                                "title": title,
                                "url": f"https://www.cls.cn{href}"
                                if href.startswith("/")
                                else href,
                                "type": "cls",
                            }
                        )

        result = {
            "data": items,
            "title": "财联社电报",
            "url": "https://www.cls.cn/telegraph",
            "total": len(items),
        }

        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result

    except Exception as e:
        return {
            "data": [],
            "title": "财联社电报",
            "url": "https://www.cls.cn/telegraph",
            "total": 0,
        }
