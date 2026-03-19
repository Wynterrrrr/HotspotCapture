from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import hashlib
import time

router = APIRouter()

def get_token():
    """获取51CTO的token"""
    cache_key = "51cto-token"
    
    cached_token = cache.get(cache_key)
    if cached_token:
        return cached_token
    
    url = "https://api-media.51cto.com/api/token-get"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        return None
    
    try:
        data = response.json()
        token = data.get("data", {}).get("data", {}).get("token", "")
        if token:
            cache.set(cache_key, token, 3600)
        return token
    except:
        return None

def sign(request_path, payload, timestamp, token):
    """生成签名"""
    payload["timestamp"] = timestamp
    payload["token"] = token
    
    sorted_params = "".join(sorted(payload.keys()))
    
    md5_request_path = hashlib.md5(request_path.encode()).hexdigest()
    md5_token = hashlib.md5(token.encode()).hexdigest()
    md5_params = hashlib.md5((sorted_params + md5_token + str(timestamp)).encode()).hexdigest()
    
    return hashlib.md5((md5_request_path + md5_params).encode()).hexdigest()

@router.get("/51cto")
async def get_51cto_hot():
    """获取51CTO推荐榜"""
    cache_key = "51cto"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    token = get_token()
    if not token:
        raise HTTPException(status_code=500, detail="获取51CTO token失败")
    
    params = {
        "page": 1,
        "page_size": 50,
        "limit_time": 0,
        "name_en": ""
    }
    
    timestamp = int(time.time() * 1000)
    
    url = "https://api-media.51cto.com/index/index/recommend"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    request_params = {
        **params,
        "timestamp": timestamp,
        "token": token,
        "sign": sign("index/index/recommend", params, timestamp, token)
    }
    
    response = get(url, headers=headers, params=request_params)
    if not response:
        raise HTTPException(status_code=500, detail="获取51CTO推荐榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("data", {}).get("list", []):
            items.append({
                "id": item.get("source_id", ""),
                "title": item.get("title", ""),
                "cover": item.get("cover", ""),
                "desc": item.get("abstract", ""),
                "timestamp": item.get("pubdate", None),
                "hot": None,
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", "")
            })
        
        result = {
            "data": items,
            "title": "51CTO",
            "type": "推荐榜",
            "url": "https://www.51cto.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析51CTO推荐榜失败: {str(e)}")