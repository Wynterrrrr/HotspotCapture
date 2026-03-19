from fastapi import APIRouter
from utils.cache import cache
from config import config

def create_route(platform: str, url: str, title: str, fetch_func):
    """
    创建标准化的路由
    :param platform: 平台名称
    :param url: 平台URL
    :param title: 标题
    :param fetch_func: 数据获取函数
    :return: APIRouter实例
    """
    router = APIRouter()
    
    @router.get(f"/{platform}")
    async def get_platform_hot():
        cache_key = platform
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            items = await fetch_func()
            result = {"data": items, "title": title, "url": url}
            cache.set(cache_key, result, config.CACHE_EXPIRE)
            return result
        except Exception as e:
            return {"data": [], "title": title, "url": url}
    
    return router