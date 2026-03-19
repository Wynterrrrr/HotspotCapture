from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/csdn")
async def get_csdn_hot():
    """获取CSDN排行榜"""
    cache_key = "csdn"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=30"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取CSDN排行榜失败")
    
    try:
        data = response.json()
        list_data = data.get("data", [])
        
        items = []
        for item in list_data:
            items.append({
                "id": item.get("productId", ""),
                "title": item.get("articleTitle", ""),
                "cover": item.get("picList", [""])[0] if item.get("picList") else "",
                "desc": None,
                "author": item.get("nickName", ""),
                "timestamp": item.get("period", None),
                "hot": int(item.get("hotRankScore", 0)) if item.get("hotRankScore") else 0,
                "url": item.get("articleDetailUrl", ""),
                "mobileUrl": item.get("articleDetailUrl", ""),
                "type": "csdn"
            })
        
        result = {
            "data": items,
            "title": "CSDN排行榜",
            "description": "专业开发者社区",
            "url": "https://www.csdn.net/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析CSDN排行榜失败: {str(e)}")