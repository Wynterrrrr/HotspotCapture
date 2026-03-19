from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import re

router = APIRouter()

def replace_link(url, get_id=False):
    """链接处理"""
    match = re.search(r'[html|live]/(\d+)\.htm', url)
    if match and match.group(1):
        id_value = match.group(1)
        if get_id:
            return id_value
        return f"https://www.ithome.com/0/{id_value[:3]}/{id_value[3:]}.htm"
    return url

@router.get("/ithome")
async def get_ithome_hot():
    """获取IT之家热榜"""
    cache_key = "ithome"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://m.ithome.com/rankm/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取IT之家热榜失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        for item in soup.select(".rank-box .placeholder"):
            title_elem = item.select_one(".plc-title")
            if title_elem:
                title = title_elem.text.strip()
                
                href_elem = item.select_one("a")
                href = href_elem.get("href", "") if href_elem else ""
                
                cover_elem = item.select_one("img")
                cover = cover_elem.get("data-original", "") if cover_elem else ""
                
                time_elem = item.select_one("span.post-time")
                timestamp = time_elem.text.strip() if time_elem else ""
                
                hot_elem = item.select_one(".review-num")
                hot_text = hot_elem.text.strip() if hot_elem else ""
                hot = int(re.sub(r'\D', '', hot_text)) if hot_text else 0
                
                url_value = replace_link(href) if href else ""
                id_value = replace_link(href, get_id=True) if href else ""
                
                items.append({
                    "id": id_value,
                    "title": title,
                    "cover": cover,
                    "timestamp": timestamp,
                    "hot": hot,
                    "url": url_value,
                    "mobileUrl": url_value,
                    "type": "ithome"
                })
        
        result = {
            "data": items,
            "title": "IT之家",
            "type": "热榜",
            "url": "https://m.ithome.com/rankm/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析IT之家热榜失败: {str(e)}")