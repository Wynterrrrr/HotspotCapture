from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/guokr")
async def get_guokr_hot():
    """获取果壳热门文章"""
    cache_key = "guokr"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.guokr.com/beta/proxy/science_api/articles?limit=30"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取果壳热门文章失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data:
            author = item.get("author", {})
            
            items.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "desc": item.get("summary"),
                "cover": item.get("small_image"),
                "author": author.get("nickname"),
                "hot": None,
                "timestamp": get_timestamp(item.get("date_modified")),
                "url": f"https://www.guokr.com/article/{item.get('id', '')}",
                "mobileUrl": f"https://m.guokr.com/article/{item.get('id', '')}"
            })
        
        result = {
            "data": items,
            "name": "guokr",
            "title": "果壳",
            "type": "热门文章",
            "description": "科技有意思",
            "link": "https://www.guokr.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析果壳热门文章失败: {str(e)}")