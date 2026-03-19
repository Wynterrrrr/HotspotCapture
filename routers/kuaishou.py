from fastapi import APIRouter
import requests
from requests.exceptions import RequestException
from utils.cache import cache
from config import config
import re
import json
from urllib.parse import unquote

router = APIRouter()

APOLLO_STATE_PREFIX = "window.__APOLLO_STATE__="

def parse_chinese_number(chinese_number: str) -> float:
    """转换中文数字为数字"""
    if not chinese_number or chinese_number == "None":
        return 0.0
    
    units = {
        "亿": 1e8,
        "万": 1e4,
        "千": 1e3,
        "百": 1e2,
    }
    
    for unit, value in units.items():
        if unit in chinese_number:
            try:
                number_part = float(chinese_number.replace(unit, ""))
                return number_part * value
            except (ValueError, TypeError):
                return 0.0
    
    try:
        return float(chinese_number)
    except (ValueError, TypeError):
        return 0.0

@router.get("/kuaishou")
async def get_kuaishou_hot():
    """获取快手热点榜"""
    cache_key = "kuaishou"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://www.kuaishou.com/?isHome=1"
    
    # 构建请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.kuaishou.com/",
        "Origin": "https://www.kuaishou.com"
    }
    
    try:
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 获取 HTML 内容
        html = response.text
        
        # 查找 APOLLO_STATE
        start = html.find(APOLLO_STATE_PREFIX)
        if start == -1:
            raise Exception("快手页面结构变更，未找到 APOLLO_STATE")
        
        # 提取 script 内容
        script_slice = html[start + len(APOLLO_STATE_PREFIX):]
        sentinel_a = script_slice.find(";(function(")
        sentinel_b = script_slice.find("</script>")
        
        if sentinel_a != -1 and sentinel_b != -1:
            cut_index = min(sentinel_a, sentinel_b)
        else:
            cut_index = max(sentinel_a, sentinel_b)
        
        if cut_index == -1:
            raise Exception("快手页面结构变更，未找到 APOLLO_STATE 结束标记")
        
        raw = script_slice[:cut_index].strip().rstrip(";")
        
        # 解析 JSON
        try:
            # 快手返回的 JSON 末尾常带 undefined/null，需要截断到最后一个 '}' 出现
            last_brace = raw.rfind("}")
            clean_raw = raw[:last_brace + 1] if last_brace != -1 else raw
            json_object = json.loads(clean_raw)["defaultClient"]
        except Exception as err:
            raise Exception(f"快手数据解析失败: {str(err)} | snippet={raw[:200]}...")
        
        # 获取所有分类
        all_items = []
        if '$ROOT_QUERY.visionHotRank({"page":"home"})' in json_object:
            all_items = json_object['$ROOT_QUERY.visionHotRank({"page":"home"})'].get('items', [])
        elif '$ROOT_QUERY.visionHotRank({"page":"home","platform":"web"})' in json_object:
            all_items = json_object['$ROOT_QUERY.visionHotRank({"page":"home","platform":"web"})'].get('items', [])
        
        # 获取全部热榜
        list_data = []
        for item in all_items:
            if not isinstance(item, dict):
                continue
            
            item_id = item.get("id")
            if not item_id:
                continue
            
            # 获取基础数据
            hot_item = json_object.get(item_id)
            if not hot_item:
                continue
            
            # 获取 photoId
            photo_ids = hot_item.get("photoIds", {})
            if isinstance(photo_ids, dict):
                photo_ids_json = photo_ids.get("json", [])
                id_value = photo_ids_json[0] if photo_ids_json else ""
            else:
                id_value = ""
            
            # 获取 hotValue
            hot_value = hot_item.get("hotValue", "")
            
            # 获取 poster 并解码
            poster = hot_item.get("poster", "")
            if poster:
                poster = unquote(poster)
            
            list_data.append({
                "id": hot_item.get("id", ""),
                "title": hot_item.get("name", ""),
                "cover": poster,
                "hot": parse_chinese_number(str(hot_value)),
                "timestamp": None,
                "url": f"https://www.kuaishou.com/short-video/{id_value}",
                "mobileUrl": f"https://www.kuaishou.com/short-video/{id_value}"
            })
        
        final_result = {
            "data": list_data,
            "title": "快手",
            "type": "热榜",
            "description": "快手，拥抱每一种生活",
            "link": "https://www.kuaishou.com/",
            "total": len(list_data)
        }
        
        # 缓存结果
        cache.set(cache_key, final_result, config.CACHE_EXPIRE)
        
        return final_result
        
    except RequestException as e:
        from utils.logger import logger
        logger.error(f"HTTP请求失败: {url} - {str(e)}")
        return {
            "data": [], 
            "title": "快手", 
            "type": "热榜",
            "description": "快手，拥抱每一种生活",
            "link": "https://www.kuaishou.com/",
            "total": 0
        }
    except Exception as e:
        from utils.logger import logger
        logger.error(f"获取快手热点榜失败: {str(e)}")
        return {
            "data": [], 
            "title": "快手", 
            "type": "热榜",
            "description": "快手，拥抱每一种生活",
            "link": "https://www.kuaishou.com/",
            "total": 0
        }