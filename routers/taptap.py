from fastapi import APIRouter
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()


@router.get("/taptap")
async def get_taptap_hot():
    """获取TapTap热榜"""
    cache_key = "taptap"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    url = (
        "https://www.taptap.cn/webapiv2/app-top/v1/hits?plat=0&type_name=hot&_api=false"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.taptap.cn/",
        "Accept": "application/json",
    }

    try:
        response = get(url, headers=headers, timeout=15)
        if not response:
            return {
                "data": [],
                "title": "TapTap热榜",
                "url": "https://www.taptap.cn/",
                "total": 0,
            }

        data = response.json()
        items = []

        for item in data.get("data", {}).get("list", []):
            app = item.get("app", {})
            items.append(
                {
                    "id": app.get("id", ""),
                    "title": app.get("title", ""),
                    "cover": app.get("icon", "").replace("rs:0:0", "rs:200:200"),
                    "author": app.get("author", {}).get("name", ""),
                    "rating": app.get("stat", {}).get("rating", {}).get("score", 0),
                    "hot": app.get("stat", {}).get("view_count", 0),
                    "url": f"https://www.taptap.cn/app/{app.get('id', '')}",
                    "type": "taptap",
                }
            )

        result = {
            "data": items,
            "title": "TapTap热榜",
            "url": "https://www.taptap.cn/",
            "total": len(items),
        }

        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result

    except Exception as e:
        # 备用方案：页面爬取
        return await fetch_from_page()


async def fetch_from_page():
    """从页面爬取TapTap热榜"""
    from bs4 import BeautifulSoup

    url = "https://www.taptap.cn/ranking/hot"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = get(url, headers=headers, timeout=15)
        if not response:
            return {"data": [], "title": "TapTap热榜", "url": url, "total": 0}

        soup = BeautifulSoup(response.text, "html.parser")
        items = []

        for item in soup.select(".app-item, .ranking-item, .taptap-app-item")[:30]:
            title_elem = item.select_one(".app-name, .name, h4")
            if title_elem:
                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")
                if not href:
                    link_elem = item.select_one("a")
                    href = link_elem.get("href", "") if link_elem else ""

                items.append(
                    {
                        "id": len(items) + 1,
                        "title": title,
                        "url": f"https://www.taptap.cn{href}"
                        if href.startswith("/")
                        else href,
                        "type": "taptap",
                    }
                )

        result = {"data": items, "title": "TapTap热榜", "url": url, "total": len(items)}

        cache.set("taptap", result, config.CACHE_EXPIRE)
        return result

    except Exception as e:
        return {"data": [], "title": "TapTap热榜", "url": url, "total": 0}
