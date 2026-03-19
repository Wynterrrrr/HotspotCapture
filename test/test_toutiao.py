import requests

response = requests.get('http://localhost:8000/toutiao')
data = response.json()
print(f"Title: {data.get('title', 'N/A')}")
print(f"Total: {data.get('total', len(data.get('data', [])))}")
if data.get('data'):
    print(f"First item: {data['data'][0].get('title', 'N/A')}")
    print(f"First item hot: {data['data'][0].get('hot', 'N/A')}")