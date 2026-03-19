from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
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

@router.get("/yystv")
async def get_yystv_hot():
    """获取游研社热门文章"""
    cache_key = "yystv"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.yystv.cn/home/get_home_docs_by_page"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.yystv.cn/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取游研社热门文章失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "cover": item.get("cover", ""),
                "author": item.get("author", ""),
                "hot": None,
                "timestamp": get_timestamp(item.get("createtime")),
                "url": f"https://www.yystv.cn/p/{item.get('id', '')}",
                "mobileUrl": f"https://www.yystv.cn/p/{item.get('id', '')}"
            })
        
        result = {
            "data": items,
            "name": "yystv",
            "title": "游研社",
            "type": "全部文章",
            "description": "游研社是以游戏内容为主的新媒体，出品内容包括大量游戏、动漫有关的研究文章和社长聊街机、社长说、游研剧场、老四强等系列视频内容。",
            "link": "https://www.yystv.cn/docs",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析游研社热门文章失败: {str(e)}")
