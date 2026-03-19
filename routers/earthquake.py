from fastapi import APIRouter, HTTPException
from utils.http import get
from utils.cache import cache
from config import config
import re
import json

router = APIRouter()

@router.get("/earthquake")
async def get_earthquake_hot():
    """获取中国地震台地震速报"""
    cache_key = "earthquake"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://news.ceic.ac.cn/speedsearch.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = get(url, headers=headers)
    if not response:
        return {"data": [], "title": "中国地震台", "type": "地震速报", "url": "https://news.ceic.ac.cn/", "total": 0}
    
    try:
        regex = r"const D=(\[.*?\]);"
        match = re.search(regex, response.text, re.DOTALL)
        list_data = []
        if match and match.group(1):
            list_data = json.loads(match.group(1))
        
        items = []
        for item in list_data:
            content_builder = []
            m = item[0]
            new_did = item[1]
            epi_lat = item[2]
            epi_lon = item[3]
            epi_depth = item[4]
            o_time = item[5]
            location_c = item[6]
            
            content_builder.append(f"发震时刻(UTC+8)：{o_time}")
            content_builder.append(f"参考位置：{location_c}")
            content_builder.append(f"震级(M)：{m}")
            content_builder.append(f"纬度(°)：{epi_lat}")
            content_builder.append(f"经度(°)：{epi_lon}")
            content_builder.append(f"深度(千米)：{epi_depth}")
            
            items.append({
                "id": new_did,
                "title": f"{location_c}发生{m}级地震",
                "desc": "\n".join(content_builder),
                "timestamp": o_time,
                "hot": None,
                "url": f"https://news.ceic.ac.cn/{new_did}.html",
                "mobileUrl": f"https://news.ceic.ac.cn/{new_did}.html"
            })
        
        result = {
            "data": items,
            "title": "中国地震台",
            "type": "地震速报",
            "url": "https://news.ceic.ac.cn/",
            "total": len(items)
        }
        
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析中国地震台数据失败: {str(e)}")