from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

game_map = {
    "1": "崩坏3",
    "2": "原神",
    "3": "崩坏学园2",
    "4": "未定事件簿",
    "5": "大别野",
    "6": "崩坏：星穹铁道",
    "7": "暂无",
    "8": "绝区零"
}

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

@router.get("/miyoushe")
async def get_miyoushe_hot(game: str = Query("1", description="游戏分类: 1(崩坏3), 2(原神), 3(崩坏学园2), 4(未定事件簿), 5(大别野), 6(崩坏：星穹铁道), 7(暂无), 8(绝区零)"), type: str = Query("1", description="榜单分类: 1(公告), 2(活动), 3(资讯)")):
    """获取米游社最新消息"""
    cache_key = f"miyoushe_{game}_{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://bbs-api-static.miyoushe.com/painter/wapi/getNewsList?client_type=4&gids={game}&last_id=&page_size=30&type={type}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取米游社最新消息失败")
    
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
                "hot": post.get("view_status", 0),
                "url": f"https://www.miyoushe.com/ys/article/{post_id}",
                "mobileUrl": f"https://m.miyoushe.com/ys/#/article/{post_id}"
            })
        
        result = {
            "data": items,
            "name": "miyoushe",
            "title": f"米游社 · {game_map.get(game, '原神')}",
            "type": f"最新{type_map.get(type, '公告')}",
            "params": {
                "game": {
                    "name": "游戏分类",
                    "type": game_map
                },
                "type": {
                    "name": "榜单分类",
                    "type": type_map
                }
            },
            "link": "https://www.miyoushe.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析米游社最新消息失败: {str(e)}")