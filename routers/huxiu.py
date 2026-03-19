from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(timestamp):
    """转换时间戳"""
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

@router.get("/huxiu")
async def get_huxiu_hot():
    """获取虎嗅24小时热榜"""
    cache_key = "huxiu"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://moment-api.huxiu.com/web-v3/moment/feed?platform=www"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.huxiu.com/moment/"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取虎嗅24小时热榜失败")
    
    try:
        json_data = response.json()
        items = []
        
        for item in json_data.get("data", {}).get("moment_list", {}).get("datalist", []):
            content = (item.get("content", "") or "").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
            content_lines = [line.strip() for line in content.split("\n") if line.strip()]
            
            title = ""
            desc = ""
            if content_lines:
                title = content_lines[0].rstrip("。")
                desc = "\n".join(content_lines[1:]) if len(content_lines) > 1 else ""
            
            moment_id = item.get("object_id")
            user_info = item.get("user_info", {})
            count_info = item.get("count_info", {})
            
            items.append({
                "id": moment_id,
                "title": title,
                "desc": desc,
                "author": user_info.get("username"),
                "timestamp": get_timestamp(item.get("publish_time")),
                "hot": count_info.get("agree_num"),
                "url": f"https://www.huxiu.com/moment/{moment_id}.html",
                "mobileUrl": f"https://m.huxiu.com/moment/{moment_id}.html"
            })
        
        result = {
            "data": items,
            "name": "huxiu",
            "title": "虎嗅",
            "type": "24小时",
            "link": "https://www.huxiu.com/moment/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析虎嗅24小时热榜失败: {str(e)}")