from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime

router = APIRouter()

def get_timestamp(created):
    """转换时间戳"""
    if not created:
        return None
    try:
        return datetime.strptime(created, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(created, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except:
            return None

@router.get("/lol")
async def get_lol_hot():
    """获取英雄联盟更新公告"""
    cache_key = "lol"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://apps.game.qq.com/cmc/zmMcnTargetContentList?r0=json&page=1&num=30&target=24&source=web_pc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取英雄联盟更新公告失败")
    
    try:
        data = response.json()
        list_data = data.get("data", {}).get("result", [])
        items = []
        
        for item in list_data:
            doc_id = item.get("iDocID", "")
            cover = item.get("sIMG", "")
            if cover and not cover.startswith("http"):
                cover = f"https:{cover}"
            
            items.append({
                "id": doc_id,
                "title": item.get("sTitle", ""),
                "cover": cover,
                "author": item.get("sAuthor", ""),
                "hot": int(item.get("iTotalPlay", 0)) if item.get("iTotalPlay") else 0,
                "timestamp": get_timestamp(item.get("sCreated")),
                "url": f"https://lol.qq.com/news/detail.shtml?docid={doc_id}",
                "mobileUrl": f"https://lol.qq.com/news/detail.shtml?docid={doc_id}"
            })
        
        result = {
            "data": items,
            "name": "lol",
            "title": "英雄联盟",
            "type": "更新公告",
            "link": "https://lol.qq.com/gicp/news/423/2/1334/1.html",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析英雄联盟更新公告失败: {str(e)}")