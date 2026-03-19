from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import re

router = APIRouter()

def get_numbers(text):
    """从字符串中提取数字"""
    if not text:
        return 0
    match = re.search(r'\d+', text)
    if match:
        return int(match.group(0))
    return 0

@router.get("/douban-movie")
async def get_douban_movie_hot():
    """获取豆瓣电影新片榜"""
    cache_key = "douban-movie"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://movie.douban.com/chart/"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取豆瓣电影新片榜失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        for item in soup.select(".article tr.item"):
            link_elem = item.select_one("a")
            if link_elem:
                url = link_elem.get("href", "")
                id_num = get_numbers(url)
                title = link_elem.get("title", "")
                cover_elem = item.select_one("img")
                cover = cover_elem.get("src", "") if cover_elem else ""
                desc_elem = item.select_one("p.pl")
                desc = desc_elem.text.strip() if desc_elem else ""
                score_elem = item.select_one(".rating_nums")
                score = score_elem.text.strip() if score_elem else "0.0"
                hot_elem = item.select_one("span.pl")
                hot = get_numbers(hot_elem.text.strip()) if hot_elem else 0
                
                items.append({
                    "id": id_num,
                    "title": f"【{score}】{title}",
                    "cover": cover,
                    "desc": desc,
                    "timestamp": None,
                    "hot": hot,
                    "url": url or f"https://movie.douban.com/subject/{id_num}/",
                    "mobileUrl": f"https://m.douban.com/movie/subject/{id_num}/"
                })
        
        result = {
            "data": items,
            "title": "豆瓣电影",
            "type": "新片榜",
            "url": "https://movie.douban.com/chart",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析豆瓣电影新片榜失败: {str(e)}")