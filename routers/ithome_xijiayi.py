from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime
import re

router = APIRouter()

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def replace_link(url, get_id=False):
    """链接处理"""
    match = re.match(r'https://www\.ithome\.com/0/(\d+)/(\d+)\.htm', url)
    if match and match.group(1) and match.group(2):
        if get_id:
            return match.group(1) + match.group(2)
        return f"https://m.ithome.com/html/{match.group(1)}{match.group(2)}.htm"
    return url

@router.get("/ithome-xijiayi")
async def get_ithome_xijiayi_hot():
    """获取 IT之家「喜加一」"""
    cache_key = "ithome-xijiayi"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.ithome.com/zt/xijiayi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取 IT之家「喜加一」失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        
        list_items = soup.select(".newslist li")
        for item in list_items:
            href_elem = item.find("a")
            time_elem = item.find("span", class_="time")
            title_elem = item.select_one(".newsbody h2")
            desc_elem = item.select_one(".newsbody p")
            img_elem = item.find("img")
            comment_elem = item.find(class_="comment")
            
            href = href_elem.get("href") if href_elem else ""
            time_text = time_elem.get_text(strip=True) if time_elem else ""
            
            timestamp = None
            if time_text:
                match = re.search(r"'([^']+)'", time_text)
                if match:
                    timestamp = get_timestamp(match.group(1))
            
            items.append({
                "id": int(replace_link(href, True)) if href else 100000,
                "title": title_elem.get_text(strip=True) if title_elem else "",
                "desc": desc_elem.get_text(strip=True) if desc_elem else "",
                "cover": img_elem.get("data-original") if img_elem else None,
                "timestamp": timestamp,
                "hot": int(re.sub(r'\D', '', comment_elem.get_text(strip=True))) if comment_elem else 0,
                "url": href,
                "mobileUrl": replace_link(href) if href else ""
            })
        
        result = {
            "data": items,
            "name": "ithome-xijiayi",
            "title": "IT之家「喜加一」",
            "type": "最新动态",
            "description": "最新最全的「喜加一」游戏动态尽在这里！",
            "link": "https://www.ithome.com/zt/xijiayi",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析 IT之家「喜加一」失败: {str(e)}")
