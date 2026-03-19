from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

def get_id(url):
    """获取 ID"""
    if not url:
        return "undefined"
    match = url.split("/")[-1]
    return match if match else "undefined"

@router.get("/jianshu")
async def get_jianshu_hot():
    """获取简书热门推荐"""
    cache_key = "jianshu"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.jianshu.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.jianshu.com"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取简书热门推荐失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        for item in soup.select("div.today-selection-list li"):
            title_elem = item.select_one("a")
            if title_elem:
                title = title_elem.text.strip()
                
                href_elem = item.select_one("a")
                href = href_elem.get("href", "") if href_elem else ""
                
                cover_elem = item.select_one("img")
                cover = cover_elem.get("src", "") if cover_elem else ""
                
                desc_elem = item.select_one("p.abstract")
                desc = desc_elem.text.strip() if desc_elem else ""
                
                author_elem = item.select_one("a.nickname")
                author = author_elem.text.strip() if author_elem else ""
                
                url_value = f"https://www.jianshu.com{href}" if href else ""
                id_value = get_id(href)
                
                items.append({
                    "id": id_value,
                    "title": title,
                    "cover": cover,
                    "desc": desc,
                    "author": author,
                    "hot": None,
                    "timestamp": None,
                    "url": url_value,
                    "mobileUrl": url_value,
                    "type": "jianshu"
                })
        
        result = {
            "data": items,
            "title": "简书",
            "type": "热门推荐",
            "url": "https://www.jianshu.com/",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析简书热门推荐失败: {str(e)}")