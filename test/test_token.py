import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from routes.coolapk import get_random_device_id, get_app_token, gen_headers

def test_token_generation():
    """测试token生成"""
    print("测试token生成...")
    
    device_id = get_random_device_id()
    print(f"Device ID: {device_id}")
    
    token = get_app_token()
    print(f"Token: {token}")
    print(f"Token length: {len(token)}")
    
    headers = gen_headers()
    print(f"Headers: {headers}")
    
    print("\n✅ Token生成测试完成")

if __name__ == "__main__":
    test_token_generation()
