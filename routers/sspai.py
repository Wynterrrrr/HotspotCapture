from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(released_time):
    """转换时间戳"""
    if not released_time:
        return None
    try:
        return datetime.fromtimestamp(released_time).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/sspai")
async def get_sspai_hot():
    """获取少数派热榜"""
    cache_key = "sspai"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://sspai.com/api/v1/article/tag/page/get?limit=40&tag=热门文章"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取少数派热榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("summary", ""),
                "cover": item.get("banner", ""),
                "author": item.get("author", {}).get("nickname", ""),
                "timestamp": get_timestamp(item.get("released_time")),
                "hot": item.get("like_count", ""),
                "url": f"https://sspai.com/post/{item.get('id', '')}",
                "mobileUrl": f"https://sspai.com/post/{item.get('id', '')}"
            })
        
        result = {
            "data": items,
            "name": "sspai",
            "title": "少数派",
            "type": "热榜",
            "params": {
                "type": {
                    "name": "分类",
                    "type": ["热门文章", "应用推荐", "生活方式", "效率技巧", "少数派播客"]
                }
            },
            "link": "https://sspai.com/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析少数派热榜失败: {str(e)}")