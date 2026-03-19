from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(create_time):
    """转换时间戳"""
    if not create_time:
        return None
    try:
        return datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/tieba")
async def get_tieba_hot():
    """获取百度贴吧热议榜"""
    cache_key = "tieba"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "http://tieba.baidu.com/hottopic/browse/topicList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取百度贴吧热议榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("bang_topic", {}).get("topic_list", []):
            items.append({
                "id": item.get("topic_id", ""),
                "title": item.get("topic_name", ""),
                "desc": item.get("topic_desc", ""),
                "cover": item.get("topic_pic", ""),
                "hot": item.get("discuss_num", ""),
                "timestamp": get_timestamp(item.get("create_time")),
                "url": item.get("topic_url", ""),
                "mobileUrl": item.get("topic_url", "")
            })
        
        result = {
            "data": items,
            "name": "tieba",
            "title": "百度贴吧",
            "type": "热议榜",
            "description": "全球领先的中文社区",
            "link": "https://tieba.baidu.com/hottopic/browse/topicList",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析百度贴吧热议榜失败: {str(e)}")