from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/geekpark")
async def get_geekpark_hot():
    """获取极客公园热门文章"""
    cache_key = "geekpark"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://mainssl.geekpark.net/api/v2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取极客公园热门文章失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("homepage_posts", []):
            post = item.get("post", {})
            authors = post.get("authors", [])
            
            items.append({
                "id": post.get("id"),
                "title": post.get("title"),
                "desc": post.get("abstract"),
                "cover": post.get("cover_url"),
                "author": authors[0].get("nickname") if authors else None,
                "hot": post.get("views"),
                "timestamp": get_timestamp(post.get("published_timestamp")),
                "url": f"https://www.geekpark.net/news/{post.get('id', '')}",
                "mobileUrl": f"https://www.geekpark.net/news/{post.get('id', '')}"
            })
        
        result = {
            "data": items,
            "name": "geekpark",
            "title": "极客公园",
            "type": "热门文章",
            "description": "极客公园聚焦互联网领域，跟踪新鲜的科技新闻动态，关注极具创新精神的科技产品。",
            "link": "https://www.geekpark.net/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析极客公园热门文章失败: {str(e)}")
