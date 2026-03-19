from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from bs4 import BeautifulSoup

router = APIRouter()


@router.get("/autohome")
async def get_autohome_hot():
    """获取汽车之家热点榜"""
    cache_key = "autohome"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    url = "https://www.autohome.com.cn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = get(url, headers=headers, timeout=15)
        if not response:
            return {"data": [], "title": "汽车之家", "url": url, "total": 0}

        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        seen_titles = set()

        # 获取热点新闻
        hot_sections = soup.select(
            ".hotbox li a, .list-cont li a, .news-list li a, .article-list a"
        )

        for item in hot_sections[:30]:
            title = item.get_text(strip=True)
            href = item.get("href", "")

            if title and len(title) > 5 and title not in seen_titles:
                seen_titles.add(title)

                if href and not href.startswith("http"):
                    href = f"https://www.autohome.com.cn{href}"

                items.append(
                    {
                        "id": len(items) + 1,
                        "title": title,
                        "url": href,
                        "type": "autohome",
                    }
                )

        result = {
            "data": items,
            "title": "汽车之家",
            "url": "https://www.autohome.com.cn/",
            "total": len(items),
        }

        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result

    except Exception as e:
        return {"data": [], "title": "汽车之家", "url": url, "total": 0}
