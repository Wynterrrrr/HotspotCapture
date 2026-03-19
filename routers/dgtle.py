from fastapi import APIRouter, HTTPException
from utils.cache import cache
from utils.http import get
from config import config

router = APIRouter()

@router.get("/dgtle")
async def get_dgtle_hot():
    cache_key = "dgtle"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = "https://opser.api.dgtle.com/v2/news/index"
    response = get(url)
    if not response:
        return {"data": [], "title": "数字尾巴", "type": "热门文章", "url": "https://www.dgtle.com/", "total": 0}
    
    try:
        data = response.json()
        items = data.get('items', [])
        
        result_items = []
        for item in items:
            result_items.append({
                "id": item.get('id'),
                "title": item.get('title') or item.get('content'),
                "desc": item.get('content'),
                "cover": item.get('cover'),
                "author": item.get('from'),
                "hot": item.get('membernum'),
                "timestamp": item.get('created_at'),
                "url": f"https://www.dgtle.com/news-{item.get('id')}-{item.get('type')}.html",
                "mobileUrl": f"https://m.dgtle.com/news-details/{item.get('id')}"
            })
        
        result = {
            "data": result_items,
            "title": "数字尾巴",
            "type": "热门文章",
            "description": "致力于分享美好数字生活体验，囊括你闻所未闻的最丰富数码资讯，触所未触最抢鲜产品评测，随时随地感受尾巴们各式数字生活精彩图文、摄影感悟、旅行游记、爱物分享。",
            "url": "https://www.dgtle.com/",
            "total": len(result_items)
        }
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析数字尾巴数据失败: {str(e)}")