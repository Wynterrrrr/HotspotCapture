from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

type_map = {
    "1": "公告",
    "2": "活动",
    "3": "资讯"
}

def get_timestamp(created_at):
    """转换时间戳"""
    if not created_at:
        return None
    try:
        return datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/starrail")
async def get_starrail_hot(type: str = Query("1", description="榜单分类: 1(公告), 2(活动), 3(资讯)")):
    """获取崩坏：星穹铁道最新动态"""
    cache_key = f"starrail_{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://bbs-api-static.miyoushe.com/painter/wapi/getNewsList?client_type=4&gids=6&page_size=20&type={type}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取崩坏：星穹铁道最新动态失败")
    
    try:
        data = response.json()
        list_data = data.get("data", {}).get("list", [])
        items = []
        
        for item in list_data:
            post = item.get("post", {})
            user = item.get("user", {})
            post_id = post.get("post_id", "")
            
            cover = post.get("cover")
            if not cover:
                images = post.get("images", [])
                if images and len(images) > 0:
                    cover = images[0]
            
            items.append({
                "id": post_id,
                "title": post.get("subject", ""),
                "desc": post.get("content", ""),
                "cover": cover,
                "author": user.get("nickname") if user else None,
                "timestamp": get_timestamp(post.get("created_at")),
                "hot": post.get("view_status"),
                "url": f"https://www.miyoushe.com/sr/article/{post_id}",
                "mobileUrl": f"https://m.miyoushe.com/sr/#/article/{post_id}"
            })
        
        result = {
            "data": items,
            "name": "starrail",
            "title": "崩坏：星穹铁道",
            "type": "最新动态",
            "params": {
                "type": {
                    "name": "榜单分类",
                    "type": type_map
                }
            },
            "link": "https://www.miyoushe.com/sr/home/53",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析崩坏：星穹铁道最新动态失败: {str(e)}")
