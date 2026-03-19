import requests

response = requests.get('http://localhost:8000/api/bilibili')
data = response.json()
print(f"Full response: {data}")