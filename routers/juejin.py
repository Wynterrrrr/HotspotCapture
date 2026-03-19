from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/juejin")
async def get_juejin_hot():
    """获取稀土掘金热门文章榜"""
    cache_key = "juejin"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    
    url = "https://api.juejin.cn/content_api/v1/content/article_rank?category_id=1&type=hot"
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取稀土掘金热门文章榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            items.append({
                "id": item.get("content", {}).get("content_id", ""),
                "title": item.get("content", {}).get("title", ""),
                "author": item.get("author", {}).get("name", ""),
                "hot": item.get("content_counter", {}).get("hot_rank", 0),
                "timestamp": None,
                "url": f"https://juejin.cn/post/{item.get('content', {}).get('content_id', '')}",
                "mobileUrl": f"https://juejin.cn/post/{item.get('content', {}).get('content_id', '')}",
                "type": "juejin"
            })
        
        result = {"data": items, "title": "稀土掘金热门文章榜", "url": "https://juejin.cn/hot/articles"}
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析稀土掘金热门文章榜失败: {str(e)}")