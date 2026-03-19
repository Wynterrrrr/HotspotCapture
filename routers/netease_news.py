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
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/netease-news")
async def get_netease_news_hot():
    """获取网易新闻热点榜"""
    cache_key = "netease-news"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://m.163.com/fe/api/hot/news/flow"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取网易新闻热点榜失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("data", {}).get("list", []):
            docid = item.get("docid")
            
            items.append({
                "id": docid,
                "title": item.get("title"),
                "cover": item.get("imgsrc"),
                "author": item.get("source"),
                "hot": None,
                "timestamp": get_timestamp(item.get("ptime")),
                "url": f"https://www.163.com/dy/article/{docid}.html",
                "mobileUrl": f"https://m.163.com/dy/article/{docid}.html"
            })
        
        result = {
            "data": items,
            "name": "netease-news",
            "title": "网易新闻",
            "type": "热点榜",
            "link": "https://m.163.com/hot",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析网易新闻热点榜失败: {str(e)}")