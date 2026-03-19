from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/zhihu-daily")
async def get_zhihu_daily_hot():
    """获取知乎日报"""
    cache_key = "zhihu-daily"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://daily.zhihu.com/api/4/news/latest"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://daily.zhihu.com/api/4/news/latest",
        "Host": "daily.zhihu.com"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取知乎日报失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("stories", []):
            if item.get("type") != 0:
                continue
            
            images = item.get("images", [])
            cover = images[0] if images else None
            
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "cover": cover,
                "author": item.get("hint", ""),
                "hot": None,
                "timestamp": None,
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", "")
            })
        
        result = {
            "data": items,
            "title": "知乎日报",
            "type": "推荐榜",
            "description": "每天三次，每次七分钟",
            "url": "https://daily.zhihu.com/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析知乎日报失败: {str(e)}")