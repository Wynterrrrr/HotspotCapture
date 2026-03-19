from fastapi import APIRouter
import requests
from requests.exceptions import RequestException
from utils.cache import cache
from config import config
import re
from datetime import datetime

router = APIRouter()

async def get_dy_cookies():
    """获取抖音临时 Cookie"""
    try:
        cookis_url = "https://www.douyin.com/passport/general/login_guiding_strategy/?aid=6383"
        response = requests.get(cookis_url, allow_redirects=False, timeout=10)
        
        if response.headers.get("set-cookie"):
            set_cookie = response.headers["set-cookie"]
            pattern = r"passport_csrf_token=(.*?);"
            match_result = re.search(pattern, set_cookie)
            if match_result:
                return match_result.group(1)
    except Exception as e:
        from utils.logger import logger
        logger.error(f"获取抖音 Cookie 出错: {str(e)}")
    return None

def get_time(timestamp):
    """转换时间戳为 datetime 对象"""
    try:
        return datetime.fromtimestamp(timestamp)
    except:
        return None

@router.get("/douyin")
async def get_douyin_hot():
    """获取抖音热点榜"""
    cache_key = "douyin"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 获取 Cookie
    cookie = await get_dy_cookies()
    
    # API URL
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1"
    
    # 构建请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.douyin.com/",
        "Origin": "https://www.douyin.com"
    }
    
    if cookie:
        headers["Cookie"] = f"passport_csrf_token={cookie}"
    
    try:
        # 创建 session 以保持 cookies
        session = requests.Session()
        
        # 发送请求
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析 JSON 响应
        result = response.json()
        
        # 获取 word_list
        word_list = result.get("data", {}).get("word_list", [])
        
        # 映射数据结构
        items = []
        for v in word_list:
            items.append({
                "id": v.get("sentence_id", ""),
                "title": v.get("word", ""),
                "timestamp": get_time(v.get("event_time", 0)),
                "hot": v.get("hot_value", ""),
                "url": f"https://www.douyin.com/hot/{v.get('sentence_id', '')}",
                "mobileUrl": f"https://www.douyin.com/hot/{v.get('sentence_id', '')}"
            })
        
        final_result = {
            "data": items,
            "title": "抖音",
            "type": "热榜",
            "description": "实时上升热点",
            "link": "https://www.douyin.com",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, final_result, config.CACHE_EXPIRE)
        
        return final_result
        
    except RequestException as e:
        from utils.logger import logger
        logger.error(f"HTTP请求失败: {url} - {str(e)}")
        return {
            "data": [], 
            "title": "抖音", 
            "type": "热榜",
            "description": "实时上升热点",
            "link": "https://www.douyin.com",
            "total": 0
        }
    except Exception as e:
        from utils.logger import logger
        logger.error(f"获取抖音热点榜失败: {str(e)}")
        return {
            "data": [], 
            "title": "抖音", 
            "type": "热榜",
            "description": "实时上升热点",
            "link": "https://www.douyin.com",
            "total": 0
        }