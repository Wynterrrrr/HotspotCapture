from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/v2ex")
async def get_v2ex_hot():
    """获取V2EX主题榜"""
    cache_key = "v2ex"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 使用API接口而不是HTML页面
    url = "https://www.v2ex.com/api/topics/hot.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取V2EX主题榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data:
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("content", ""),
                "author": item.get("member", {}).get("username", ""),
                "timestamp": None,
                "hot": item.get("replies", 0),
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", ""),
                "type": "v2ex"
            })
        
        result = {"data": items, "title": "V2EX主题榜", "url": "https://www.v2ex.com/"}
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析V2EX主题榜失败: {str(e)}")