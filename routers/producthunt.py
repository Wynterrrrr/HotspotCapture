from fastapi import APIRouter, HTTPException
from utils.cache import cache
from config import config

router = APIRouter()

@router.get("/producthunt")
async def get_producthunt_hot():
    cache_key = "producthunt"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    base_url = "https://www.producthunt.com"
    url = base_url
    
    import cloudscraper
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url, timeout=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Product Hunt数据失败: {str(e)}")
    
    if not response or response.status_code != 200:
        raise HTTPException(status_code=500, detail="获取Product Hunt数据失败")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = []
    post_items = soup.select("section[data-test^=post-item-]")
    
    for item in post_items:
        data_test = item.get("data-test", "")
        id_value = data_test.replace("post-item-", "") if data_test else ""
        
        title_elem = item.select_one("span[data-test^=post-name-]")
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        link_elem = item.select_one('a[href^="/products/"]')
        path = link_elem.get("href") if link_elem else ""
        
        vote_elem = item.select_one("button[data-test=vote-button]")
        vote_text = vote_elem.get_text(strip=True) if vote_elem else ""
        hot = int(vote_text) if vote_text else None
        
        if path and id_value and title:
            items.append({
                "id": id_value,
                "title": title,
                "hot": hot,
                "timestamp": None,
                "url": f"{base_url}{path}",
                "mobileUrl": f"{base_url}{path}"
            })
    
    result = {
        "data": items,
        "name": "producthunt",
        "title": "Product Hunt",
        "type": "Today",
        "description": "The best new products, every day",
        "link": url,
        "total": len(items)
    }
    
    cache.set(cache_key, result, config.CACHE_EXPIRE)
    return result