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
        return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/thepaper")
async def get_thepaper_hot():
    """获取澎湃新闻热榜"""
    cache_key = "thepaper"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取澎湃新闻热榜失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("data", {}).get("hotNews", []):
            cont_id = item.get("contId")
            
            items.append({
                "id": cont_id,
                "title": item.get("name"),
                "cover": item.get("pic"),
                "hot": int(item.get("praiseTimes", 0)),
                "timestamp": get_timestamp(item.get("pubTimeLong")),
                "url": f"https://www.thepaper.cn/newsDetail_forward_{cont_id}",
                "mobileUrl": f"https://m.thepaper.cn/newsDetail_forward_{cont_id}"
            })
        
        result = {
            "data": items,
            "name": "thepaper",
            "title": "澎湃新闻",
            "type": "热榜",
            "link": "https://www.thepaper.cn/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析澎湃新闻热榜失败: {str(e)}")