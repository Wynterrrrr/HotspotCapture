from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/hackernews")
async def get_hackernews_hot():
    """获取Hacker News热点"""
    cache_key = "hackernews"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取Hacker News热点失败")
    
    try:
        item_ids = response.json()[:20]  # 获取前20条
        items = []
        
        for item_id in item_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
            item_response = get(item_url, headers=headers)
            if item_response:
                item_data = item_response.json()
                items.append({
                    "title": item_data.get("title", ""),
                    "url": item_data.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                    "hot": item_data.get("score", ""),
                    "id": item_id,
                    "type": "hackernews"
                })
        
        result = {"data": items, "title": "Hacker News热点", "url": "https://news.ycombinator.com/"}
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析Hacker News热点失败: {str(e)}")