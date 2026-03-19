from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import post
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

@router.get("/ngabbs")
async def get_ngabbs_hot():
    """获取 NGA 玩家社区热门话题"""
    cache_key = "ngabbs"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://ngabbs.com/nuke.php?__lib=load_topic&__act=load_topic_reply_ladder2&opt=1&all=1"
    headers = {
        "Accept": "*/*",
        "Host": "ngabbs.com",
        "Referer": "https://ngabbs.com/",
        "Connection": "keep-alive",
        "Content-Length": "11",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-Hans-CN;q=1",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "X-User-Agent": "NGA_skull/7.3.1(iPhone13,2;iOS 17.2.1)"
    }
    data = {
        "__output": "14"
    }
    
    response = post(url, headers=headers, data=data)
    if not response:
        raise HTTPException(status_code=500, detail="获取 NGA 玩家社区热门话题失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("result", [])[0]:
            items.append({
                "id": item.get("tid"),
                "title": item.get("subject"),
                "author": item.get("author"),
                "hot": item.get("replies"),
                "timestamp": get_timestamp(item.get("postdate")),
                "url": f"https://bbs.nga.cn{item.get('tpurl', '')}",
                "mobileUrl": f"https://bbs.nga.cn{item.get('tpurl', '')}"
            })
        
        result = {
            "data": items,
            "name": "ngabbs",
            "title": "NGA",
            "type": "论坛热帖",
            "description": "精英玩家俱乐部",
            "link": "https://ngabbs.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析 NGA 玩家社区热门话题失败: {str(e)}")
