# PyDailyHotApi

> 一个聚合热门数据的 API 接口，支持 60+ 个主流平台热点数据抓取

## 功能特性

- **多平台支持**：微博、知乎、哔哩哔哩、抖音、GitHub、豆瓣等 60+ 个平台
- **RESTful API**：基于 FastAPI 构建，支持 Swagger 文档
- **定时抓取**：每日四次自动抓取（6:00/11:00/16:00/21:00 北京时间）
- **AI 分析**：集成大模型进行热点深度分析
- **GitHub 同步**：自动推送热点汇总到 GitHub 仓库
- **缓存机制**：内置缓存系统，减少重复请求

## 支持平台

| 类别 | 平台 |
|------|------|
| 社交媒体 | 微博、知乎、贴吧、豆瓣小组、小红书、Reddit |
| 视频平台 | 哔哩哔哩、抖音、快手、AcFun |
| 新闻资讯 | 今日头条、腾讯新闻、网易新闻、新浪新闻、澎湃新闻、财联社 |
| 科技资讯 | 36氪、虎嗅、少数派、爱范儿、IT之家、极客公园 |
| 开发者社区 | GitHub、掘金、CSDN、V2EX、HostLoc、LinuxDo、NodeSeek |
| 游戏相关 | TapTap、游民星空、虎扑、原神、崩坏、星穹铁道、LOL |
| 其他 | 百度热搜、豆瓣电影、地震速报、历史今日、天气预警 |

## 快速开始

### 环境要求

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (推荐) 或 pip

### 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/HotspotCapture.git
cd HotspotCapture

# 安装依赖 (使用 uv)
uv install

# 或使用 pip
pip install -e .
```

### 配置

创建 `.env` 文件：

```env
# 服务器配置
PORT=6688
HOST=0.0.0.0

# 缓存配置（秒）
CACHE_EXPIRE=3600

# CORS 配置
ALLOWED_DOMAIN=*
```

### 运行

**启动 API 服务：**

```bash
# 使用 uv
uv run uvicorn main:app --host 0.0.0.0 --port 6688

# 或
uv run python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=6688)"
```

**运行定时抓取：**

```bash
uv run python scheduler.py
```

访问 http://localhost:6688/docs 查看 API 文档。

## API 示例

### 获取微博热搜

```bash
curl http://localhost:6688/weibo
```

响应示例：

```json
{
  "data": [
    {
      "title": "热点标题",
      "url": "https://weibo.com/search?q=xxx",
      "hot": 123456,
      "id": "xxx",
      "type": "weibo"
    }
  ],
  "title": "微博热搜榜",
  "url": "https://weibo.com/hot/search"
}
```

### 其他接口

| 路径 | 平台 |
|------|------|
| `/weibo` | 微博热搜榜 |
| `/bilibili` | 哔哩哔哩热门 |
| `/zhihu` | 知乎热榜 |
| `/douyin` | 抖音热点 |
| `/github` | GitHub Trending |
| `/toutiao` | 今日头条 |
| `/juejin` | 掘金热门 |
| `/douban_movie` | 豆瓣电影 |
| `/health` | 健康检查 |

## 项目结构

```
HotspotCapture/
├── main.py              # FastAPI 应用入口
├── config.py            # 配置管理
├── registry.py          # 路由注册中心
├── scheduler.py         # 定时抓取调度器
├── deepseek_thinker.py  # AI 深度分析模块
├── routers/             # 各平台数据源路由
│   ├── weibo.py
│   ├── bilibili.py
│   ├── zhihu.py
│   └── ...              # 60+ 个平台
├── utils/               # 工具模块
│   ├── http.py          # HTTP 请求封装
│   ├── cache.py         # 缓存系统
│   ├── logger.py        # 日志模块
│   └── base_route.py    # 路由基类
├── test/                # 测试文件
├── deploy/              # 部署配置
│   └── DEPLOY.md        # 部署指南
└── pyproject.toml       # 项目配置
```

## 定时任务部署

详细部署指南请参考 [deploy/DEPLOY.md](deploy/DEPLOY.md)

### Systemd Timer（推荐）

```bash
# 复制服务文件
sudo cp deploy/hotnews-scheduler.service /etc/systemd/system/

# 创建并启用定时器
sudo systemctl enable hotnews-scheduler.timer
sudo systemctl start hotnews-scheduler.timer
```

### Crontab

```cron
0 6 * * * cd /opt/HotspotCapture && uv run python scheduler.py
0 11 * * * cd /opt/HotspotCapture && uv run python scheduler.py
0 16 * * * cd /opt/HotspotCapture && uv run python scheduler.py
0 21 * * * cd /opt/HotspotCapture && uv run python scheduler.py
```

## AI 深度分析

项目集成了 AI 深度分析功能，支持：

- **火山引擎**：DeepSeek V3、GLM-4、DeepSeek R1
- **SiliconFlow**：备用接口

分析内容包括：
- 热点事件类型和趋势总结
- 跨平台热点关联分析
- 重要社会议题识别
- 阅读建议和思考方向

## 开发

### 添加新平台

1. 在 `routers/` 目录创建新文件 `new_platform.py`

2. 实现数据获取函数：

```python
from fastapi import APIRouter
from utils.http import get
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/new_platform")
async def get_new_platform_hot():
    """获取新平台热点"""
    cache_key = "new_platform"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 实现数据获取逻辑
    items = []
    # ...
    
    result = {"data": items, "title": "新平台热榜", "url": "https://..."}
    cache.set(cache_key, result, config.CACHE_EXPIRE)
    
    return result
```

3. 在 `registry.py` 中注册模块名

### 运行测试

```bash
uv run python test/test_weibo.py
```

## 技术栈

- **框架**：FastAPI + Uvicorn
- **HTTP 客户端**：Requests + HTTPX
- **HTML 解析**：BeautifulSoup4
- **浏览器自动化**：Playwright（部分平台）
- **反爬处理**：Cloudscraper
- **包管理**：uv

## 许可证

MIT License

## 致谢

本项目受 [DailyHot](https://github.com/DailyHot/DailyHot) 启发。
