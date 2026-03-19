import time

class Cache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        """获取缓存值"""
        if key in self.cache:
            value, expire = self.cache[key]
            if time.time() < expire:
                return value
            else:
                # 缓存过期，删除
                del self.cache[key]
        return None
    
    def set(self, key, value, expire=3600):
        """设置缓存值"""
        self.cache[key] = (value, time.time() + expire)
    
    def delete(self, key):
        """删除缓存值"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()

# 创建全局缓存实例
cache = Cache()