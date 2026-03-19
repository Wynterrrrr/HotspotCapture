from fastapi import APIRouter, HTTPException, Query
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime

router = APIRouter()

SORT_MAP = {
    "featured": "精选",
    "all": "全部"
}

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/hellogithub")
async def get_hellogithub_hot(sort: str = Query("featured", description="排行榜分区")):
    """获取 HelloGitHub 热门仓库"""
    if sort not in SORT_MAP:
        raise HTTPException(status_code=400, detail=f"无效的排行榜分区: {sort}")
    
    cache_key = f"hellogithub-{sort}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://abroad.hellogithub.com/v1/?sort_by={sort}&tid=&page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取 HelloGitHub 热门仓库失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("data", []):
            items.append({
                "id": item.get("item_id"),
                "title": item.get("title"),
                "desc": item.get("summary"),
                "author": item.get("author"),
                "timestamp": get_timestamp(item.get("updated_at")),
                "hot": item.get("clicks_total"),
                "url": f"https://hellogithub.com/repository/{item.get('item_id', '')}",
                "mobileUrl": f"https://hellogithub.com/repository/{item.get('item_id', '')}"
            })
        
        result = {
            "data": items,
            "name": "hellogithub",
            "title": "HelloGitHub",
            "type": "热门仓库",
            "description": "分享 GitHub 上有趣、入门级的开源项目",
            "params": {
                "sort": {
                    "name": "排行榜分区",
                    "type": SORT_MAP
                }
            },
            "link": "https://hellogithub.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析 HelloGitHub 热门仓库失败: {str(e)}")
