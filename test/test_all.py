import requests

endpoints = [
    "/bilibili",
    "/weibo",
    "/zhihu",
    "/juejin",
    "/v2ex",
    "/github",
    "/csdn",
    "/toutiao",
    "/baidu",
]

base_url = "http://localhost:8000"

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}")
        data = response.json()
        total = data.get("total", len(data.get("data", [])))
        title = data.get("title", "N/A")
        print(f"{endpoint}: {title} - Total: {total}")
    except Exception as e:
        print(f"{endpoint}: Error - {str(e)}")