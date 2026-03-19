from fastapi import APIRouter, HTTPException, Query
from utils.http import get
from utils.cache import cache
from config import config
import time

router = APIRouter()

@router.get("/github")
async def get_github_hot(type_param: str = Query(default="daily", description="榜单类型: daily, weekly, monthly")):
    """获取GitHub Trending"""
    cache_key = f"github-{type_param}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    type_map = {
        "daily": "日榜",
        "weekly": "周榜",
        "monthly": "月榜"
    }
    
    if type_param not in type_map:
        type_param = "daily"
    
    url = f"https://github.com/trending?since={type_param}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    response = get(url, headers=headers, timeout=20)
    if not response:
        raise HTTPException(status_code=500, detail="获取GitHub Trending失败")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        items = []
        
        for index, item in enumerate(soup.select("article.Box-row")):
            repo_anchor = item.select_one("h2 a")
            if repo_anchor:
                full_name_text = repo_anchor.text.strip().replace("\r\n", "").replace("\n", "").replace("\r", "").replace("\t", "").replace("  ", " ")
                parts = full_name_text.split("/")
                owner = parts[0].strip() if len(parts) > 0 else ""
                repo_name = parts[1].strip() if len(parts) > 1 else ""
                
                repo_url = f"https://github.com{repo_anchor.get('href', '')}"
                
                description_elem = item.select_one("p.col-9.color-fg-muted")
                description = description_elem.text.strip() if description_elem else ""
                
                language_elem = item.select_one('[itemprop="programmingLanguage"]')
                language = language_elem.text.strip() if language_elem else ""
                
                stars_elem = item.select_one('a[href$="/stargazers"]')
                stars = stars_elem.text.strip() if stars_elem else ""
                
                forks_elem = item.select_one('a[href$="/forks"]')
                forks = forks_elem.text.strip() if forks_elem else ""
                
                items.append({
                    "id": index,
                    "title": repo_name,
                    "desc": description,
                    "owner": owner,
                    "repo": repo_name,
                    "url": repo_url,
                    "language": language,
                    "stars": stars,
                    "forks": forks,
                    "hot": stars,
                    "type": "github"
                })
        
        result = {
            "data": items,
            "title": "github 趋势",
            "type": type_map[type_param],
            "url": f"https://github.com/trending?since={type_param}",
            "total": len(items)
        }
        
        # 缓存结果
        cache.set(cache_key, result, config.CACHE_EXPIRE)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析GitHub Trending失败: {str(e)}")