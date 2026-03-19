from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
from config import config
from registry import router
from utils.logger import logger

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.ALLOWED_DOMAIN == "*" else config.ALLOWED_DOMAIN.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/public", StaticFiles(directory="public"), name="public")

# 注册路由
app.include_router(router)

# 首页
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PyDailyHotApi - 今日热榜</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 40px;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 40px;
            }
            .api-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            .api-item {
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                transition: all 0.3s ease;
            }
            .api-item:hover {
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .api-item h3 {
                margin-top: 0;
                color: #4a90e2;
            }
            .api-item p {
                margin-bottom: 15px;
                color: #666;
            }
            .api-item a {
                display: inline-block;
                padding: 8px 16px;
                background-color: #4a90e2;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }
            .api-item a:hover {
                background-color: #357abd;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PyDailyHotApi - 今日热榜</h1>
            <div class="api-list">
                <div class="api-item">
                    <h3>微博热搜榜</h3>
                    <p>获取微博实时热搜榜单</p>
                    <a href="/weibo" target="_blank">查看数据</a>
                </div>
                <div class="api-item">
                    <h3>哔哩哔哩热门榜</h3>
                    <p>获取哔哩哔哩视频热门榜单</p>
                    <a href="/bilibili" target="_blank">查看数据</a>
                </div>
                <div class="api-item">
                    <h3>知乎热榜</h3>
                    <p>获取知乎实时热榜</p>
                    <a href="/zhihu" target="_blank">查看数据</a>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>PyDailyHotApi v1.0.0 - 一个聚合热门数据的 API 接口</p>
        </div>
    </body>
    </html>
    """

# 404处理
@app.get("/{path:path}")
async def not_found(path: str):
    return {
        "error": "404 Not Found",
        "message": f"路径 '{path}' 不存在",
        "available_endpoints": [
            "/weibo",
            "/bilibili",
            "/zhihu",
            "/health"
        ]
    }