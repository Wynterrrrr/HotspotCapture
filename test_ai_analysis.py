"""
AI Analysis Module Test
"""

import asyncio
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass

from deepseek_thinker import run_deep_analysis, VOLC_MODELS, VOLC_BASE_URL, VOLC_API_KEY
import httpx


async def test_simple_call():
    """Test simple API call"""
    print("=" * 50)
    print("Testing API Connection")
    print("=" * 50)

    async with httpx.AsyncClient() as client:
        for model in VOLC_MODELS:
            print(f"\nTesting model: {model}")
            success, result = await asyncio.wait_for(
                asyncio.create_task(_test_single_model(client, model)), timeout=30.0
            )
            if success:
                print(f"[OK] {model} SUCCESS!")
                print(f"   Response: {result[:100]}...")
                return True
            else:
                print(f"[FAIL] {model} Failed: {result}")

    print("\nAll models failed")
    return False


async def _test_single_model(client: httpx.AsyncClient, model: str) -> tuple:
    """Test single model"""
    headers = {
        "Authorization": f"Bearer {VOLC_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'test success' in Chinese"}],
        "max_tokens": 50,
    }
    url = f"{VOLC_BASE_URL}/chat/completions"

    try:
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)
        if response.status_code == 200:
            data = response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, result
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, str(e)


async def test_full_analysis():
    """Test full analysis flow"""
    print("\n" + "=" * 50)
    print("Testing Full Analysis")
    print("=" * 50)

    test_content = """
# Test Hot News

## Weibo Hot
1. Test news 1
2. Test news 2

## Bilibili Hot
1. Test video 1
2. Test video 2
"""

    result = await run_deep_analysis(
        test_content, Path(__file__).parent / "hotnews_output", datetime.now()
    )

    print(f"\nGenerated file: {result}")
    return result


if __name__ == "__main__":
    print("AI Analysis Module Test\n")

    # Test simple call
    success = asyncio.run(test_simple_call())

    # Ask to continue
    print("\n" + "-" * 50)
    try:
        user_input = input("Run full analysis test? (y/n): ")
        if user_input.lower() == "y":
            asyncio.run(test_full_analysis())
        else:
            print("Skipped full test")
    except EOFError:
        print("Skipped full test")
