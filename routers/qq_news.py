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
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/qq-news")
async def get_qq_news_hot():
    """获取腾讯新闻热点榜"""
    cache_key = "qq-news"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://r.inews.qq.com/gw/event/hot_ranking_list?page_size=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取腾讯新闻热点榜失败")
    
    try:
        data = response.json()
        items = []
        
        newslist = data.get("idlist", [{}])[0].get("newslist", [])[1:]
        
        for item in newslist:
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "desc": item.get("abstract", ""),
                "cover": item.get("miniProShareImage", ""),
                "author": item.get("source", ""),
                "hot": item.get("hotEvent", {}).get("hotScore", ""),
                "timestamp": get_timestamp(item.get("timestamp")),
                "url": f"https://new.qq.com/rain/a/{item.get('id', '')}",
                "mobileUrl": f"https://view.inews.qq.com/k/{item.get('id', '')}"
            })
        
        result = {
            "data": items,
            "name": "qq-news",
            "title": "腾讯新闻",
            "type": "热点榜",
            "link": "https://news.qq.com/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析腾讯新闻热点榜失败: {str(e)}")