from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

TYPE_MAP = {
    "1": "今日热门",
    "7": "周热门",
    "30": "月热门"
}

def get_timestamp(time_sort):
    """转换时间戳"""
    if not time_sort:
        return None
    try:
        return datetime.fromtimestamp(time_sort).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/smzdm")
async def get_smzdm_hot():
    """获取什么值得买热榜"""
    cache_key = "smzdm"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    type_value = "1"
    url = f"https://post.smzdm.com/rank/json_more/?unit={type_value}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.smzdm.com/top/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取什么值得买热榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            items.append({
                "id": item.get("article_id", ""),
                "title": item.get("title", ""),
                "desc": item.get("content", ""),
                "cover": item.get("pic_url", ""),
                "author": item.get("nickname", ""),
                "hot": int(item.get("collection_count", 0)) if item.get("collection_count") else 0,
                "timestamp": get_timestamp(item.get("time_sort")),
                "url": item.get("jump_link", ""),
                "mobileUrl": item.get("jump_link", "")
            })
        
        result = {
            "data": items,
            "name": "smzdm",
            "title": "什么值得买",
            "type": TYPE_MAP.get(type_value, "今日热门"),
            "description": "什么值得买是一个中立的、致力于帮助广大网友买到更有性价比网购产品的最热门推荐网站。",
            "link": "https://www.smzdm.com/top/",
            "params": {
                "type": {
                    "name": "文章分类",
                    "type": TYPE_MAP
                }
            },
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析什么值得买热榜失败: {str(e)}")