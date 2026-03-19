from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
from datetime import datetime
import re

router = APIRouter()

LIST_TYPE = {
    "1": {"name": "总排行", "www": "news", "params": "www_www_all_suda_suda"},
    "2": {"name": "视频排行", "www": "news", "params": "video_news_all_by_vv"},
    "3": {"name": "图片排行", "www": "news", "params": "total_slide_suda"},
    "4": {"name": "国内新闻", "www": "news", "params": "news_china_suda"},
    "5": {"name": "国际新闻", "www": "news", "params": "news_world_suda"},
    "6": {"name": "社会新闻", "www": "news", "params": "news_society_suda"},
    "7": {"name": "体育新闻", "www": "sports", "params": "sports_suda"},
    "8": {"name": "财经新闻", "www": "finance", "params": "finance_0_suda"},
    "9": {"name": "娱乐新闻", "www": "ent", "params": "ent_suda"},
    "10": {"name": "科技新闻", "www": "tech", "params": "tech_news_suda"},
    "11": {"name": "军事新闻", "www": "news", "params": "news_mil_suda"},
}

def get_timestamp(date_str):
    """转换时间戳"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def parse_jsonp(data):
    """解析 JSONP 响应"""
    if not data:
        raise ValueError("Input data is empty or invalid")
    
    prefix = "var data = "
    if not data.startswith(prefix):
        raise ValueError("Input data does not start with the expected prefix")
    
    json_string = data[len(prefix):].strip()
    
    if json_string.endswith(";"):
        json_string = json_string[:-1].strip()
    else:
        raise ValueError("Input data does not end with a semicolon")
    
    if json_string.startswith("{") and json_string.endswith("}"):
        import json
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
    else:
        raise ValueError("Invalid JSON format")

@router.get("/sina-news")
async def get_sina_news_hot(type: str = Query("1", description="榜单分类")):
    """获取新浪新闻热点榜"""
    if type not in LIST_TYPE:
        raise HTTPException(status_code=400, detail=f"无效的榜单分类: {type}")
    
    cache_key = f"sina-news-{type}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    list_info = LIST_TYPE[type]
    www = list_info["www"]
    params = list_info["params"]
    
    now = datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    
    url = f"https://top.{www}.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat={params}&top_time={year}{month}{day}&top_show_num=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取新浪新闻热点榜失败")
    
    try:
        parsed_data = parse_jsonp(response.text)
        items = []
        
        for item in parsed_data.get("data", []):
            hot_num = item.get("top_num", "0")
            try:
                hot = float(hot_num.replace(",", ""))
            except:
                hot = 0
            
            create_date = item.get("create_date", "")
            create_time = item.get("create_time", "")
            timestamp = get_timestamp(f"{create_date} {create_time}")
            
            items.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "author": item.get("media") or None,
                "hot": hot,
                "timestamp": timestamp,
                "url": item.get("url", ""),
                "mobileUrl": item.get("url", "")
            })
        
        result = {
            "data": items,
            "name": "sina-news",
            "title": "新浪新闻",
            "type": list_info["name"],
            "params": {
                "type": {
                    "name": "榜单分类",
                    "type": {k: v["name"] for k, v in LIST_TYPE.items()}
                }
            },
            "link": "https://sinanews.sina.cn/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析新浪新闻热点榜失败: {str(e)}")
