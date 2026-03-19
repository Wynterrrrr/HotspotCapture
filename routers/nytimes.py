from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime
import xml.etree.ElementTree as ET

router = APIRouter()

area_map = {
    "china": "中文网",
    "global": "全球版"
}

def get_timestamp(pub_date):
    """转换时间戳"""
    if not pub_date:
        return None
    try:
        return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def parse_rss(xml_text):
    """解析 RSS"""
    try:
        root = ET.fromstring(xml_text)
        items = []
        
        for item in root.findall(".//item"):
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            author = item.find("author")
            pub_date = item.find("pubDate")
            guid = item.find("guid")
            
            desc = ""
            if description is not None and description.text:
                desc = description.text.strip()
            
            items.append({
                "title": title.text if title is not None else "",
                "link": link.text if link is not None else "",
                "description": desc,
                "author": author.text if author is not None else None,
                "pubDate": pub_date.text if pub_date is not None else "",
                "guid": guid.text if guid is not None else None
            })
        
        return items
    except Exception as e:
        raise ValueError(f"Failed to parse RSS: {e}")

@router.get("/nytimes")
async def get_nytimes_hot(area: str = Query("china", description="地区分类: china(中文网) 或 global(全球版)")):
    """获取纽约时报热点"""
    cache_key = f"nytimes_{area}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://cn.nytimes.com/rss/" if area == "china" else "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取纽约时报热点失败")
    
    try:
        rss_items = parse_rss(response.text)
        items = []
        
        for i, item in enumerate(rss_items):
            link = item.get("link", "")
            items.append({
                "id": item.get("guid") or i,
                "title": item.get("title", ""),
                "desc": item.get("description", ""),
                "author": item.get("author"),
                "timestamp": get_timestamp(item.get("pubDate")),
                "hot": None,
                "url": link,
                "mobileUrl": link
            })
        
        result = {
            "data": items,
            "name": "nytimes",
            "title": "纽约时报",
            "type": area_map.get(area, "中文网"),
            "params": {
                "area": {
                    "name": "地区分类",
                    "type": area_map
                }
            },
            "link": "https://www.nytimes.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析纽约时报热点失败: {str(e)}")
