import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 服务器配置
    PORT = int(os.getenv("PORT", 6688))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # 缓存配置
    CACHE_EXPIRE = int(os.getenv("CACHE_EXPIRE", 3600))  # 默认缓存1小时
    
    # CORS配置
    ALLOWED_HOST = os.getenv("ALLOWED_HOST")
    ALLOWED_DOMAIN = os.getenv("ALLOWED_DOMAIN", "*")
    
    # 应用配置
    APP_NAME = "PyDailyHotApi"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "一个聚合热门数据的 API 接口"
    APP_URL = os.getenv("APP_URL", "http://localhost:6688")

config = Config()