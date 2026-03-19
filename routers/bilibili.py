from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/bilibili")
async def get_bilibili_hot():
    """获取哔哩哔哩热门榜"""
    cache_key = "bilibili"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 使用备用接口（不需要WBI签名）
    url = "https://api.bilibili.com/x/web-interface/ranking?jsonp=jsonp?rid=0&type=all&callback=__jp0"
    headers = {
        "Referer": "https://www.bilibili.com/ranking/all",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取哔哩哔哩热门榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("list", []):
            items.append({
                "id": item.get("bvid", ""),
                "title": item.get("title", ""),
                "desc": item.get("desc", "该视频暂无简介"),
                "cover": item.get("pic", "").replace("http:", "https:"),
                "author": item.get("author", ""),
                "timestamp": None,
                "hot": item.get("video_review", 0),
                "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                "mobileUrl": f"https://m.bilibili.com/video/{item.get('bvid', '')}",
                "type": "bilibili"
            })
        
        result = {"data": items, "title": "哔哩哔哩热门榜", "url": "https://www.bilibili.com/ranking"}
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析哔哩哔哩热门榜失败: {str(e)}")