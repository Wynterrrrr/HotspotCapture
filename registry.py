from fastapi import APIRouter
import importlib

# 创建主路由
router = APIRouter()

# 导入并注册各网站路由
modules = [
    "weibo",
    "bilibili",
    "zhihu",
    "baidu",
    "douyin",
    "kuaishou",
    "hupu",
    "tieba",
    "toutiao",
    "qq_news",
    "sina_news",
    "netease_news",
    "36kr",
    "ithome",
    "csdn",
    "ifanr",
    "huxiu",
    "guokr",
    "sspai",
    "51cto",
    "acfun",
    "coolapk",
    "52pojie",
    "jianshu",
    "juejin",
    "smzdm",
    "thepaper",
    "v2ex",
    "hackernews",
    "nytimes",
    "github",
    "douban_group",
    "douban_movie",
    "genshin",
    "honkai",
    "starrail",
    "lol",
    "gameres",
    "miyoushe",
    "earthquake",
    "history",
    "weatheralarm",
    "zhihu_daily",
    "hostloc",
    "dgtle",
    "geekpark",
    "hellogithub",
    "ithome_xijiayi",
    "linuxdo",
    "newsmth",
    "ngabbs",
    "nodeseek",
    "producthunt",
    "weread",
    "yystv",
    # 新增平台
    "autohome",
    "gamersky",
    "cls",
    "taptap",
]

for module_name in modules:
    try:
        module = importlib.import_module(f"routers.{module_name}")
        if hasattr(module, "router"):
            router.include_router(module.router)
    except Exception as e:
        print(f"导入模块 {module_name} 失败: {e}")


# 健康检查
@router.get("/health")
async def health_check():
    return {"status": "ok"}
