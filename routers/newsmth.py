from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config
from datetime import datetime
from urllib.parse import quote

router = APIRouter()

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/newsmth")
async def get_newsmth_hot():
    """获取水木社区热门话题"""
    cache_key = "newsmth"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://wap.newsmth.net/wap/api/hot/global"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取水木社区热门话题失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("data", {}).get("topics", []):
            post = item.get("article", {})
            board = item.get("board", {})
            topic_id = post.get("topicId")
            board_title = board.get("title", "")
            encoded_title = quote(board_title)
            url = f"https://wap.newsmth.net/article/{topic_id}?title={encoded_title}&from=home"
            
            items.append({
                "id": item.get("firstArticleId"),
                "title": post.get("subject"),
                "desc": post.get("body"),
                "cover": None,
                "author": post.get("account", {}).get("name"),
                "hot": None,
                "timestamp": get_timestamp(post.get("postTime")),
                "url": url,
                "mobileUrl": url
            })
        
        result = {
            "data": items,
            "name": "newsmth",
            "title": "水木社区",
            "type": "热门话题",
            "description": "水木社区是一个源于清华的高知社群。",
            "link": "https://www.newsmth.net/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析水木社区热门话题失败: {str(e)}")
