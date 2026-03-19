from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

type_map = {
    "-1": "综合",
    "155": "番剧",
    "1": "动画",
    "60": "娱乐",
    "201": "生活",
    "58": "音乐",
    "123": "舞蹈·偶像",
    "59": "游戏",
    "70": "科技",
    "68": "影视",
    "69": "体育",
    "125": "鱼塘",
}

range_map = {
    "DAY": "今日",
    "THREE_DAYS": "三日",
    "WEEK": "本周",
}

@router.get("/acfun")
async def get_acfun_hot(type_param: str = Query(default="-1", description="频道ID"), range_param: str = Query(default="DAY", description="时间范围")):
    """获取AcFun排行榜"""
    if type_param not in type_map:
        type_param = "-1"
    if range_param not in range_map:
        range_param = "DAY"
    
    cache_key = f"acfun-{type_param}-{range_param}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    channel_id = "" if type_param == "-1" else type_param
    url = f"https://www.acfun.cn/rest/pc-direct/rank/channel?channelId={channel_id}&rankLimit=30&rankPeriod={range_param}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://www.acfun.cn/rank/list/?cid=-1&pcid={type_param}&range={range_param}"
    }
    
    response = get(url, headers=headers)
    if not response:
        raise HTTPException(status_code=500, detail="获取AcFun排行榜失败")
    
    try:
        data = response.json()
        items = []
        
        rank_list = data.get("rankList", [])
        for item in rank_list:
            items.append({
                "id": item.get("dougaId", ""),
                "title": item.get("contentTitle", ""),
                "desc": item.get("contentDesc", ""),
                "cover": item.get("coverUrl", ""),
                "author": item.get("userName", ""),
                "timestamp": item.get("contributeTime", 0),
                "hot": item.get("likeCount", 0),
                "url": f"https://www.acfun.cn/v/ac{item.get('dougaId', '')}",
                "mobileUrl": f"https://m.acfun.cn/v/?ac={item.get('dougaId', '')}",
                "type": "acfun"
            })
        
        result = {
            "data": items,
            "title": "AcFun",
            "type": f"排行榜 · {type_map.get(type_param, '综合')}",
            "url": "https://www.acfun.cn/rank/list/",
            "total": len(items),
            "params": {
                "type": {
                    "name": "频道",
                    "type": type_map
                },
                "range": {
                    "name": "时间",
                    "type": range_map
                }
            }
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析AcFun排行榜失败: {str(e)}")