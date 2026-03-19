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
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/ifanr")
async def get_ifanr_hot():
    """获取爱范儿快讯"""
    cache_key = "ifanr"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://sso.ifanr.com/api/v5/wp/buzz/?limit=20&offset=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取爱范儿快讯失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("objects", []):
            post_id = item.get("post_id")
            buzz_original_url = item.get("buzz_original_url")
            
            items.append({
                "id": item.get("id"),
                "title": item.get("post_title"),
                "desc": item.get("post_content"),
                "timestamp": get_timestamp(item.get("created_at")),
                "hot": item.get("like_count") or item.get("comment_count"),
                "url": buzz_original_url or f"https://www.ifanr.com/{post_id}",
                "mobileUrl": buzz_original_url or f"https://www.ifanr.com/digest/{post_id}"
            })
        
        result = {
            "data": items,
            "name": "ifanr",
            "title": "爱范儿",
            "type": "快讯",
            "description": "15秒了解全球新鲜事",
            "link": "https://www.ifanr.com/digest/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析爱范儿快讯失败: {str(e)}")