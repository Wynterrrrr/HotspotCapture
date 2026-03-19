import requests

response = requests.get('http://localhost:8000/juejin')
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")