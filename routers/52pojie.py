from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
import xml.etree.ElementTree as ET
from datetime import datetime

router = APIRouter()

TYPE_MAP = {
    "digest": "最新精华",
    "hot": "最新热门",
    "new": "最新回复",
    "newthread": "最新发表"
}

def parse_timestamp(text):
    """解析时间戳"""
    if not text:
        return None
    try:
        dt = datetime.strptime(text, "%a, %d %b %Y %H:%M:%S %z")
        return int(dt.timestamp() * 1000)
    except:
        return None

@router.get("/52pojie")
async def get_52pojie_hot(type: str = Query("digest", description="榜单分类")):
    """获取吾爱破解榜单"""
    cache_key = f"52pojie-{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://www.52pojie.cn/forum.php?mod=guide&view={type}&rss=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取吾爱破解榜单失败")
    
    try:
        decoded_content = response.content.decode('gbk', errors='ignore')
        
        root = ET.fromstring(decoded_content)
        items = []
        
        for item in root.findall(".//item"):
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            pub_date = item.find("pubDate")
            author = item.find("author")
            
            if title is not None:
                title_text = title.text or ""
                link_text = link.text if link is not None else ""
                desc_text = description.text if description is not None else ""
                pub_date_text = pub_date.text if pub_date is not None else ""
                author_text = author.text if author is not None else ""
                
                items.append({
                    "id": link_text,
                    "title": title_text,
                    "desc": desc_text.strip() if desc_text else "",
                    "author": author_text,
                    "timestamp": parse_timestamp(pub_date_text),
                    "hot": None,
                    "url": link_text,
                    "mobileUrl": link_text
                })
        
        result = {
            "data": items,
            "title": "吾爱破解",
            "type": TYPE_MAP.get(type, "最新精华"),
            "params": {
                "type": {
                    "name": "榜单分类",
                    "type": TYPE_MAP
                }
            },
            "url": "https://www.52pojie.cn/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析吾爱破解榜单失败: {str(e)}")