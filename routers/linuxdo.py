from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime
import xml.etree.ElementTree as ET

router = APIRouter()

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

@router.get("/linuxdo")
async def get_linuxdo_hot():
    """获取 LinuxDo 热门文章"""
    cache_key = "linuxdo"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://linux.do/top.rss?period=weekly"
    headers = {
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取 LinuxDo 热门文章失败")
    
    try:
        rss_items = parse_rss(response.text)
        items = []
        
        for i, item in enumerate(rss_items):
            link = item.get("link", "")
            items.append({
                "id": item.get("guid") or link or i,
                "title": item.get("title", ""),
                "desc": item.get("description", ""),
                "author": item.get("author"),
                "timestamp": get_timestamp(item.get("pubDate")),
                "url": link,
                "mobileUrl": link,
                "hot": None
            })
        
        result = {
            "data": items,
            "name": "linuxdo",
            "title": "Linux.do",
            "type": "热门文章",
            "description": "Linux 技术社区热搜",
            "link": "https://linux.do/top/weekly",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析 LinuxDo 热门文章失败: {str(e)}")
