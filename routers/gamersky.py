from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()


@router.get("/gamersky")
async def get_gamersky_hot():
    """获取游民星空热点榜"""
    cache_key = "gamersky"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    url = "https://api.gamersky.com.cn/palminterface/v2/hotnews?parentIds=0,1&nodeIds=0,1&pageIndex=1&pageSize=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.gamersky.com/",
    }

    try:
        response = get(url, headers=headers, timeout=15)
        if not response:
            return {
                "data": [],
                "title": "游民星空",
                "url": "https://www.gamersky.com/",
                "total": 0,
            }

        data = response.json()
        items = []

        for item in data.get("data", {}).get("list", []):
            items.append(
                {
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "cover": item.get("images", {}).get("url", "")
                    if item.get("images")
                    else "",
                    "hot": item.get("viewCount", 0),
                    "commentCount": item.get("commentCount", 0),
                    "url": item.get(
                        "htmlUrl",
                        f"https://www.gamersky.com/news/{item.get('id', '')}.shtml",
                    ),
                    "type": "gamersky",
                }
            )

        result = {
            "data": items,
            "title": "游民星空",
            "url": "https://www.gamersky.com/",
            "total": len(items),
        }

        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result

    except Exception as e:
        return {
            "data": [],
            "title": "游民星空",
            "url": "https://www.gamersky.com/",
            "total": 0,
        }
