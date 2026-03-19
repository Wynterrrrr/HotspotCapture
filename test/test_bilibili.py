import requests

response = requests.get('http://localhost:8000/bilibili')
data = response.json()
print(f"Title: {data['title']}")
print(f"Total: {len(data['data'])}")
if data['data']:
    print(f"First item: {data['data'][0]['title']}")