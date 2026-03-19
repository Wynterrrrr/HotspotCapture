from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

type_map = {
    "1": "主干道",
    "6": "恋爱区",
    "11": "校园区",
    "12": "历史区",
    "612": "摄影区",
}

@router.get("/hupu")
async def get_hupu_hot(type_param: str = Query(default="1", description="榜单分类")):
    """获取虎扑步行街热帖"""
    if type_param not in type_map:
        type_param = "1"
    
    cache_key = f"hupu-{type_param}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://m.hupu.com/api/v2/bbs/topicThreads?topicId={type_param}&page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取虎扑步行街热帖失败")
    
    try:
        data = response.json()
        items = []
        
        topic_threads = data.get("data", {}).get("topicThreads", [])
        for item in topic_threads:
            items.append({
                "id": item.get("tid", ""),
                "title": item.get("title", ""),
                "author": item.get("username", ""),
                "hot": item.get("replies", 0),
                "timestamp": None,
                "url": f"https://bbs.hupu.com/{item.get('tid', '')}.html",
                "mobileUrl": item.get("url", ""),
                "type": "hupu"
            })
        
        result = {
            "data": items,
            "title": "虎扑",
            "type": "步行街热帖",
            "url": "https://bbs.hupu.com/all-gambia",
            "total": len(items),
            "params": {
                "type": {
                    "name": "榜单分类",
                    "type": type_map
                }
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析虎扑步行街热帖失败: {str(e)}")