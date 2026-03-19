from fastapi import APIRouter
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/zhihu")
async def get_zhihu_hot():
    """获取知乎热榜"""
    cache_key = "zhihu"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://api.zhihu.com/topstory/hot-lists/total?limit=50"
    
    # 构建请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 如果配置了知乎 Cookie，则添加到请求头
    if hasattr(config, 'ZHIHU_COOKIE') and config.ZHIHU_COOKIE:
        headers["Cookie"] = config.ZHIHU_COOKIE
    
    response = get(url, headers=headers)
    if not response:
        return {"data": [], "title": "知乎热榜", "url": "https://www.zhihu.com/hot"}
    
    try:
        result = response.json()
        list_data = result.get("data", [])
        
        items = []
        for item in list_data:
            target = item.get("target", {})
            question_id = target.get("url", "").split("/")[-1] if target.get("url") else ""
            
            # 提取热度值
            detail_text = item.get("detail_text", "")
            hot_value = 0
            if detail_text:
                hot_part = detail_text.split(" ")[0]
                if hot_part:
                    try:
                        hot_value = float(hot_part) * 10000
                    except ValueError:
                        pass
            
            # 提取封面图片
            cover = ""
            if item.get("children") and len(item.get("children", [])) > 0:
                cover = item.get("children", [])[0].get("thumbnail", "")
            
            items.append({
                "id": target.get("id", ""),
                "title": target.get("title", ""),
                "desc": target.get("excerpt", ""),
                "cover": cover,
                "timestamp": target.get("created", 0),
                "hot": hot_value,
                "url": f"https://www.zhihu.com/question/{question_id}" if question_id else "",
                "mobileUrl": f"https://www.zhihu.com/question/{question_id}" if question_id else "",
                "type": "zhihu"
            })
        
        final_result = {
            "data": items,
            "title": "知乎热榜",
            "url": "https://www.zhihu.com/hot",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, final_result, config.CACHE_EXPIRE)
        
        return final_result
    except Exception as e:
        return {"data": [], "title": "知乎热榜", "url": "https://www.zhihu.com/hot"}