from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime
import xml.etree.ElementTree as ET

router = APIRouter()

TYPE_MAP = {
    "hot": "最新热门",
    "digest": "最新精华",
    "new": "最新回复",
    "newthread": "最新发表"
}

def get_timestamp(pub_date):
    """转换时间戳"""
    if not pub_date:
        return None
    try:
        return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
        except:
            return None

@router.get("/hostloc")
async def get_hostloc_hot(type: str = Query("hot", description="榜单分类: hot(最新热门), digest(最新精华), new(最新回复), newthread(最新发表)")):
    """获取全球主机交流榜单"""
    if type not in TYPE_MAP:
        raise HTTPException(status_code=400, detail=f"无效的榜单分类: {type}")
    
    cache_key = f"hostloc-{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://hostloc.com/forum.php?mod=guide&view={type}&rss=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取全球主机交流榜单失败")
    
    try:
        root = ET.fromstring(response.text)
        items = []
        
        for i, item in enumerate(root.findall(".//item")):
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
                "id": guid.text if guid is not None else i,
                "title": title.text if title is not None else "",
                "desc": desc,
                "author": author.text if author is not None else "",
                "timestamp": get_timestamp(pub_date.text if pub_date is not None else None),
                "hot": None,
                "url": link.text if link is not None else "",
                "mobileUrl": link.text if link is not None else ""
            })
        
        result = {
            "data": items,
            "name": "hostloc",
            "title": "全球主机交流",
            "type": TYPE_MAP[type],
            "params": {
                "type": {
                    "name": "榜单分类",
                    "type": TYPE_MAP
                }
            },
            "link": "https://hostloc.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析全球主机交流榜单失败: {str(e)}")