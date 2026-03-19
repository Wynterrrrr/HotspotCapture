from fastapi import APIRouter, HTTPException, Query
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime

router = APIRouter()

TYPE_MAP = {
    "rising": "飙升榜",
    "hot_search": "热搜榜",
    "newbook": "新书榜",
    "general_novel_rising": "小说榜",
    "all": "总榜"
}

def get_weread_id(book_id):
    """转换微信读书ID"""
    return book_id

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/weread")
async def get_weread_hot(type: str = Query("rising", description="排行榜分区")):
    """获取微信读书热门榜单"""
    if type not in TYPE_MAP:
        raise HTTPException(status_code=400, detail=f"无效的排行榜分区: {type}")
    
    cache_key = f"weread-{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://weread.qq.com/web/bookListInCategory/{type}?rank=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
        "Referer": "https://weread.qq.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取微信读书热门榜单失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("books", []):
            book_info = item.get("bookInfo", {})
            cover = book_info.get("cover", "").replace("s_", "t9_")
            
            items.append({
                "id": book_info.get("bookId", ""),
                "title": book_info.get("title", ""),
                "author": book_info.get("author", ""),
                "desc": book_info.get("intro", ""),
                "cover": cover,
                "timestamp": get_timestamp(book_info.get("publishTime")),
                "hot": item.get("readingCount"),
                "url": f"https://weread.qq.com/web/bookDetail/{get_weread_id(book_info.get('bookId', ''))}",
                "mobileUrl": f"https://weread.qq.com/web/bookDetail/{get_weread_id(book_info.get('bookId', ''))}"
            })
        
        result = {
            "data": items,
            "name": "weread",
            "title": "微信读书",
            "type": TYPE_MAP[type],
            "params": {
                "type": {
                    "name": "排行榜分区",
                    "type": TYPE_MAP
                }
            },
            "link": "https://weread.qq.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析微信读书热门榜单失败: {str(e)}")
