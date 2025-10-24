import aiohttp
import asyncio

API_BASE = "https://api.asi-alliance.ai"
POSSIBLE_PATHS = [
    "/",
    "/predict",
    "/analyze",
    "/v1/analyze",
    "/v1/predict",
    "/api/predict",
    "/api/analyze",
]

async def test_endpoint(path):
    url = API_BASE + path
    payload = {
        "volatility": 0.5,
        "collateral_ratio": 1.2,
        "leverage": 2.0,
        "asset_price": 2000,
        "market_trend": 0.1,
    }
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=10) as resp:
                print(f"{url} -> {resp.status}")
                if resp.status == 200:
                    data = await resp.text()
                    print(f"✅ Response: {data}")
                    return True
        except Exception as e:
            print(f"❌ {url} failed: {e}")
    return False

async def main():
    for path in POSSIBLE_PATHS:
        ok = await test_endpoint(path)
        if ok:
            print(f"🎯 Working endpoint found: {API_BASE + path}")
            break
    else:
        print("❌ No working endpoint found among tested paths.")

if __name__ == "__main__":
    asyncio.run(main())
