from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config
import re

router = APIRouter()

def parse_timestamp(text):
    """解析时间戳"""
    if not text:
        return None
    try:
        from datetime import datetime
        if "分钟前" in text:
            minutes = int(re.search(r'\d+', text).group(0))
            return int((datetime.now().timestamp() - minutes * 60) * 1000)
        elif "小时前" in text:
            hours = int(re.search(r'\d+', text).group(0))
            return int((datetime.now().timestamp() - hours * 3600) * 1000)
        elif "天前" in text:
            days = int(re.search(r'\d+', text).group(0))
            return int((datetime.now().timestamp() - days * 86400) * 1000)
        elif "今天" in text:
            time_match = re.search(r'(\d{1,2}):(\d{1,2})', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                now = datetime.now()
                today = datetime(now.year, now.month, now.day, hour, minute)
                return int(today.timestamp() * 1000)
        elif "昨天" in text:
            time_match = re.search(r'(\d{1,2}):(\d{1,2})', text)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                now = datetime.now()
                yesterday = datetime(now.year, now.month, now.day, hour, minute)
                yesterday = yesterday.replace(day=yesterday.day - 1)
                return int(yesterday.timestamp() * 1000)
        else:
            return None
    except:
        return None

@router.get("/gameres")
async def get_gameres_hot():
    cache_key = "gameres"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.gameres.com"
    response = get(url)
    if not response:
        return {"data": [], "title": "GameRes 游资网", "type": "最新资讯", "url": "https://www.gameres.com", "total": 0}
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        container = soup.select_one('div[data-news-pane-id="100000"]')
        if not container:
            return {"data": [], "title": "GameRes 游资网", "type": "最新资讯", "url": "https://www.gameres.com", "total": 0}
        
        items = []
        list_dom = container.select("article.feed-item")
        
        for item in list_dom:
            title_elem = item.select_one(".feed-item-title-a")
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            href = title_elem.get("href", "")
            url = href if href.startswith("http") else f"https://www.gameres.com{href}"
            
            cover_elem = item.select_one(".thumb")
            cover = cover_elem.get("data-original", "") if cover_elem else ""
            
            desc_elem = item.select_one(".feed-item-right > p")
            desc = desc_elem.get_text(strip=True) if desc_elem else ""
            
            mark_info = item.select_one(".mark-info")
            timestamp = None
            if mark_info:
                date_time = mark_info.contents[0].get_text(strip=True) if mark_info.contents else ""
                timestamp = parse_timestamp(date_time)
            
            items.append({
                "id": url,
                "title": title,
                "desc": desc,
                "cover": cover,
                "timestamp": timestamp,
                "hot": None,
                "url": url,
                "mobileUrl": url
            })
        
        result = {
            "data": items,
            "title": "GameRes 游资网",
            "type": "最新资讯",
            "description": "面向游戏从业者的游戏开发资讯，旨在为游戏制作人提供游戏研发类的程序技术、策划设计、艺术设计、原创设计等资讯内容。",
            "url": "https://www.gameres.com",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析GameRes游资网数据失败: {str(e)}")