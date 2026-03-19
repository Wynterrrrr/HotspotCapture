from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
import datetime

router = APIRouter()

@router.get("/history")
async def get_history_hot(month: int = Query(default=None, description="月份"), day: int = Query(default=None, description="日期")):
    """获取历史上的今天"""
    # 如果没有提供月份和日期，使用当前日期
    if not month or not day:
        today = datetime.date.today()
        month = today.month
        day = today.day
    
    cache_key = f"history-{month}-{day}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    month_str = str(month).zfill(2)
    day_str = str(day).zfill(2)
    
    url = f"https://baike.baidu.com/cms/home/eventsOnHistory/{month_str}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取历史上的今天失败")
    
    try:
        data = response.json()
        items = []
        
        month_data = data.get(month_str, {})
        day_data = month_data.get(f"{month_str}{day_str}", [])
        
        for index, item in enumerate(day_data):
            from bs4 import BeautifulSoup
            
            title = BeautifulSoup(item.get("title", ""), "html.parser").get_text(strip=True)
            desc = BeautifulSoup(item.get("desc", ""), "html.parser").get_text(strip=True)
            cover = item.get("pic_share", "") if item.get("cover") else None
            
            items.append({
                "id": index,
                "title": title,
                "cover": cover,
                "desc": desc,
                "year": item.get("year", ""),
                "timestamp": None,
                "hot": None,
                "url": item.get("link", ""),
                "mobileUrl": item.get("link", "")
            })
        
        result = {
            "data": items,
            "title": "历史上的今天",
            "type": f"{month}-{day}",
            "params": {
                "month": "月份",
                "day": "日期"
            },
            "url": "https://baike.baidu.com/calendar",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析历史上的今天失败: {str(e)}")