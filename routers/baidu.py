from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
import re

router = APIRouter()

@router.get("/baidu")
async def get_baidu_hot(type_param: str = Query(default="realtime", description="热搜类别: realtime, novel, movie, teleplay, car, game")):
    """获取百度热搜榜"""
    cache_key = f"baidu-{type_param}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    type_map = {
        "realtime": "热搜",
        "novel": "小说",
        "movie": "电影",
        "teleplay": "电视剧",
        "car": "汽车",
        "game": "游戏"
    }
    
    if type_param not in type_map:
        type_param = "realtime"
    
    url = f"https://top.baidu.com/board?tab={type_param}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/605.1.15"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取百度热搜榜失败")
    
    try:
        pattern = re.compile(r'<!--s-data:(.*?)-->', re.DOTALL)
        match_result = pattern.search(response.text)
        
        if not match_result:
            raise HTTPException(status_code=500, detail="解析百度热搜榜失败: 未找到数据")
        
        json_data = match_result.group(1)
        import json
        parsed_data = json.loads(json_data)
        content = parsed_data.get("cards", [{}])[0].get("content", [{}])[0].get("content", [])
        
        items = []
        for item in content:
            items.append({
                "id": item.get("index", ""),
                "title": item.get("word", ""),
                "desc": item.get("desc", ""),
                "cover": item.get("img", ""),
                "author": item.get("show", "") if item.get("show") else "",
                "timestamp": 0,
                "hot": int(item.get("hotScore", 0)) if item.get("hotScore") else 0,
                "url": f"https://www.baidu.com/s?wd={item.get('word', '')}",
                "mobileUrl": item.get("url", ""),
                "type": "baidu"
            })
        
        result = {
            "data": items,
            "title": "百度",
            "type": type_map[type_param],
            "url": "https://top.baidu.com/board",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析百度热搜榜失败: {str(e)}")