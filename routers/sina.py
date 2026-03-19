from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

type_map = {
    "all": "新浪热榜",
    "hotcmnt": "热议榜",
    "minivideo": "视频热榜",
    "ent": "娱乐热榜",
    "ai": "AI热榜",
    "auto": "汽车热榜",
    "mother": "育儿热榜",
    "fashion": "时尚热榜",
    "travel": "旅游热榜",
    "esg": "ESG热榜",
}

@router.get("/sina")
async def get_sina_hot(type: str = Query(default="all", description="榜单分类")):
    """获取新浪热榜"""
    cache_key = f"sina-{type}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://newsapp.sina.cn/api/hotlist?newsId=HB-1-snhs%2Ftop_news_list-{type}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取新浪热榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("data", {}).get("hotList", []):
            base = item.get("base", {})
            info = item.get("info", {})
            items.append({
                "title": info.get("title", ""),
                "url": base.get("base", {}).get("url", ""),
                "hot": info.get("hotValue", ""),
                "id": base.get("base", {}).get("uniqueId", ""),
                "type": "sina"
            })
        
        result = {
            "data": items, 
            "title": "新浪网", 
            "type": type_map.get(type, "新浪热榜"),
            "url": "https://sinanews.sina.cn/"
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析新浪热榜失败: {str(e)}")