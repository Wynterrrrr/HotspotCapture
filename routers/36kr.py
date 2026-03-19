from fastapi import APIRouter
import requests
from requests.exceptions import RequestException
from utils.cache import cache
from config import config
import time

router = APIRouter()

# 类型映射
type_map = {
    "hot": "人气榜",
    "video": "视频榜",
    "comment": "热议榜",
    "collect": "收藏榜"
}

# 列表类型映射
list_type_map = {
    "hot": "hotRankList",
    "video": "videoList",
    "comment": "remarkList",
    "collect": "collectList"
}

@router.get("/36kr")
async def get_36kr_hot(type: str = "hot"):
    """获取36氪热榜"""
    # 验证类型参数
    if type not in type_map:
        type = "hot"
    
    cache_key = f"36kr_{type}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://gateway.36kr.com/api/mis/nav/home/nav/rank/{type}"
    
    # 构建请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构建请求体
    body = {
        "partner_id": "wap",
        "param": {
            "siteId": 1,
            "platformId": 2
        },
        "timestamp": int(time.time() * 1000)
    }
    
    # 直接使用 requests 库发送 POST 请求
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        from utils.logger import logger
        logger.error(f"HTTP请求失败: {url} - {str(e)}")
        return {
            "data": [], 
            "title": "36氪热榜", 
            "url": "https://www.36kr.com/hot",
            "type": type_map.get(type, "人气榜")
        }
    
    try:
        result = response.json()
        
        # 确保 result 是字典类型
        if not isinstance(result, dict):
            return {
                "data": [], 
                "title": "36氪热榜", 
                "url": "https://www.36kr.com/hot",
                "type": type_map.get(type, "人气榜")
            }
        
        # 获取数据列表
        items = []
        data_dict = result.get("data", {})
        list_key = list_type_map.get(type, "hotRankList")
        data_list = data_dict.get(list_key, [])
        
        # 确保 data_list 是列表类型
        if isinstance(data_list, list):
            for item in data_list:
                # 确保 item 是字典类型
                if isinstance(item, dict):
                    template_material = item.get("templateMaterial", {})
                    if isinstance(template_material, dict):
                        items.append({
                            "id": item.get("itemId", ""),
                            "title": template_material.get("widgetTitle", ""),
                            "cover": template_material.get("widgetImage", ""),
                            "author": template_material.get("authorName", ""),
                            "timestamp": item.get("publishTime", 0),
                            "hot": template_material.get("statCollect", ""),
                            "url": f"https://www.36kr.com/p/{item.get('itemId', '')}",
                            "mobileUrl": f"https://m.36kr.com/p/{item.get('itemId', '')}",
                            "type": "36kr"
                        })
        
        final_result = {
            "data": items,
            "title": "36氪热榜",
            "url": "https://www.36kr.com/hot",
            "type": type_map.get(type, "人气榜"),
            "total": len(items),
            "params": {
                "type": {
                    "name": "热榜分类",
                    "type": type_map
                }
            }
        }
        
        # 缓存结果
        cache.set(cache_key, final_result, config.CACHE_EXPIRE)
        
        return final_result
    except Exception as e:
        return {
            "data": [], 
            "title": "36氪热榜", 
            "url": "https://www.36kr.com/hot",
            "type": type_map.get(type, "人气榜")
        }