from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/toutiao")
async def get_toutiao_hot():
    """获取今日头条热榜"""
    cache_key = "toutiao"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取今日头条热榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            cluster_id = item.get("ClusterIdStr", "")
            items.append({
                "id": cluster_id,
                "title": item.get("Title", ""),
                "cover": item.get("Image", {}).get("url", "") if item.get("Image") else "",
                "timestamp": None,
                "hot": int(item.get("HotValue", 0)) if item.get("HotValue") else 0,
                "url": f"https://www.toutiao.com/trending/{cluster_id}/" if cluster_id else "",
                "mobileUrl": f"https://api.toutiaoapi.com/feoffline/amos_land/new/html/main/index.html?topic_id={cluster_id}" if cluster_id else "",
                "type": "toutiao"
            })
        
        result = {
            "data": items,
            "title": "今日头条热榜",
            "url": "https://www.toutiao.com/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析今日头条热榜失败: {str(e)}")