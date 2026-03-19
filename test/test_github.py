import requests

response = requests.get('http://localhost:8000/github')
data = response.json()
print(f"Title: {data.get('title', 'N/A')}")
print(f"Type: {data.get('type', 'N/A')}")
print(f"Total: {data.get('total', len(data.get('data', [])))}")
if data.get('data'):
    print(f"First item: {data['data'][0].get('title', 'N/A')}")
    print(f"First item stars: {data['data'][0].get('stars', 'N/A')}")