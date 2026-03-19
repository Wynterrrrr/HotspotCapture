from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/weibo")
async def get_weibo_hot():
    """获取微博热搜榜"""
    cache_key = "weibo"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://weibo.com/ajax/statuses/hot_band"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://weibo.com/hot/search"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取微博热搜榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("band_list", []):
            items.append({
                "title": item.get("note", ""),
                "url": f"https://weibo.com/search?q={item.get('word', '')}",
                "hot": item.get("num", ""),
                "id": item.get("id", ""),
                "type": "weibo"
            })
        
        result = {"data": items, "title": "微博热搜榜", "url": "https://weibo.com/hot/search"}
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析微博热搜榜失败: {str(e)}")