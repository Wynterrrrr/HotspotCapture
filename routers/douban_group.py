from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import re

router = APIRouter()

def get_numbers(text):
    """从字符串中提取数字"""
    if not text:
        return 100000000
    match = re.search(r'\d+', text)
    if match:
        return int(match.group(0))
    return 100000000

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

@router.get("/douban-group")
async def get_douban_group_hot():
    """获取豆瓣讨论小组讨论精选"""
    cache_key = "douban-group"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.douban.com/group/explore"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取豆瓣讨论小组讨论精选失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        for item in soup.select(".article .channel-item"):
            title_elem = item.select_one("h3 a")
            if title_elem:
                title = title_elem.text.strip()
                url = title_elem.get("href", "")
                cover_elem = item.select_one(".pic-wrap img")
                cover = cover_elem.get("src", "") if cover_elem else ""
                desc_elem = item.select_one(".block p")
                desc = desc_elem.text.strip() if desc_elem else ""
                time_elem = item.select_one("span.pubtime")
                time_text = time_elem.text.strip() if time_elem else ""
                timestamp = parse_timestamp(time_text)
                id_num = get_numbers(url)
                
                items.append({
                    "id": id_num,
                    "title": title,
                    "cover": cover,
                    "desc": desc,
                    "timestamp": timestamp,
                    "hot": 0,
                    "url": url or f"https://www.douban.com/group/topic/{id_num}",
                    "mobileUrl": f"https://m.douban.com/group/topic/{id_num}/"
                })
        
        result = {
            "data": items,
            "title": "豆瓣讨论",
            "type": "讨论精选",
            "url": "https://www.douban.com/group/explore",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析豆瓣讨论小组讨论精选失败: {str(e)}")