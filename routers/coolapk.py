from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import hashlib
import random
import time
import base64

router = APIRouter()

def get_random_device_id():
    """获取随机的DEVICE_ID"""
    id_lengths = [10, 6, 6, 6, 14]
    parts = []
    for length in id_lengths:
        random_str = ""
        while len(random_str) < length:
            random_str += str(random.random())[2:]
        parts.append(random_str[:length])
    return "-".join(parts)

def get_app_token():
    """获取APP_TOKEN"""
    device_id = get_random_device_id()
    now = int(time.time())
    hex_now = "0x" + hex(now)[2:]
    md5_now = hashlib.md5(str(now).encode()).hexdigest()
    
    s = f"token://com.coolapk.market/c67ef5943784d09750dcfbb31020f0ab?{md5_now}${device_id}&com.coolapk.market"
    md5_s = hashlib.md5(base64.b64encode(s.encode())).hexdigest()
    
    token = md5_s + device_id + hex_now
    return token

def gen_headers():
    """生成请求头"""
    return {
        "X-Requested-With": "XMLHttpRequest",
        "X-App-Id": "com.coolapk.market",
        "X-App-Token": get_app_token(),
        "X-Sdk-Int": "29",
        "X-Sdk-Locale": "zh-CN",
        "X-App-Version": "11.0",
        "X-Api-Version": "11",
        "X-App-Code": "2101202",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mi 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.15 Mobile Safari/537.36"
    }

@router.get("/coolapk")
async def get_coolapk_hot():
    """获取酷安热榜"""
    cache_key = "coolapk"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://api.coolapk.com/v6/page/dataList?url=/feed/statList?cacheExpires=300&statType=day&sortField=detailnum&title=今日热门&title=今日热门&subTitle=&page=1"
    headers = gen_headers()
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取酷安热榜失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", []):
            items.append({
                "id": item.get("id", ""),
                "title": item.get("message", ""),
                "cover": item.get("tpic", ""),
                "author": item.get("username", ""),
                "desc": item.get("ttitle", ""),
                "timestamp": None,
                "hot": None,
                "url": item.get("shareUrl", ""),
                "mobileUrl": item.get("shareUrl", "")
            })
        
        result = {
            "data": items,
            "title": "酷安",
            "type": "热榜",
            "url": "https://www.coolapk.com/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析酷安热榜失败: {str(e)}")