from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from urllib.parse import quote
import re

router = APIRouter()

def parse_timestamp(text):
    """解析时间戳"""
    if not text:
        return None
    try:
        from datetime import datetime
        match = re.match(r'(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2})', text)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            dt = datetime(year, month, day, hour, minute, 0)
            return int(dt.timestamp() * 1000)
        match = re.match(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', text)
        if match:
            year, month, day, hour, minute, second = map(int, match.groups())
            dt = datetime(year, month, day, hour, minute, second)
            return int(dt.timestamp() * 1000)
        return None
    except:
        return None

@router.get("/weatheralarm")
async def get_weatheralarm_hot(province: str = Query(None, description="省份名称（例如：广东省）")):
    """获取中央气象台全国气象预警"""
    cache_key = f"weatheralarm-{province or 'all'}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    province_param = quote(province) if province and isinstance(province, str) else ""
    url = f"http://www.nmc.cn/rest/findAlarm?pageNo=1&pageSize=20&signaltype=&signallevel=&province={province_param}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取中央气象台全国气象预警失败")
    
    try:
        data = response.json()
        items = []
        
        for item in data.get("data", {}).get("page", {}).get("list", []):
            issue_time = item.get("issuetime", "")
            title = item.get("title", "")
            
            items.append({
                "id": item.get("alertid", ""),
                "title": title,
                "desc": f"{issue_time} {title}",
                "cover": item.get("pic", ""),
                "timestamp": parse_timestamp(issue_time),
                "hot": None,
                "url": f"http://nmc.cn{item.get('url', '')}",
                "mobileUrl": f"http://nmc.cn{item.get('url', '')}"
            })
        
        result = {
            "data": items,
            "title": "中央气象台",
            "type": f"{province or '全国'}气象预警",
            "params": {
                "province": {
                    "name": "预警区域",
                    "value": "省份名称（例如：广东省）"
                }
            },
            "url": "http://nmc.cn/publish/alarm.html",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析中央气象台全国气象预警失败: {str(e)}")