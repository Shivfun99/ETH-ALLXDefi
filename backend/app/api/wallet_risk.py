"""
wallet_risk.py
Fetches live wallet data (price, volatility, leverage, collateral ratio)
from CoinGecko and Aave public API.
"""

from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import statistics

router = APIRouter()


class WalletRequest(BaseModel):
    wallet_address: str


@router.post("/wallet-risk")
async def wallet_risk(req: WalletRequest):
    wallet = req.wallet_address.lower().strip()
    print(f"[DEBUG] Fetching risk data for wallet: {wallet}")

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            # 1️⃣ Fetch ETH price
            price_resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            )
            eth_price = price_resp.json().get("ethereum", {}).get("usd", 0)
        except httpx.ReadTimeout:
            print("[WARN] CoinGecko price API timed out — using fallback value")
            eth_price = 2000
        except Exception as e:
            print(f"[WARN] Price fetch failed: {e}")
            eth_price = 2000

        try:
            # 2️⃣ Fetch ETH 7-day volatility
            hist_resp = await client.get(
                "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=7"
            )
            hist_data = hist_resp.json()
            prices = [p[1] for p in hist_data.get("prices", [])]
            volatility = (
                round(statistics.stdev(prices) / statistics.mean(prices), 4)
                if len(prices) > 1
                else 0
            )
        except httpx.ReadTimeout:
            print("[WARN] CoinGecko volatility API timed out — using default 0.3")
            prices = [2000, 2050, 2100]
            volatility = 0.3
        except Exception as e:
            print(f"[WARN] Volatility fetch failed: {e}")
            prices = [2000, 2050, 2100]
            volatility = 0.3

        # 3️⃣ Fetch Aave user data (using Aave v3 subgraph)
        query = f"""
        {{
          userReserves(where: {{user: "{wallet}"}}) {{
            reserve {{
              symbol
              liquidityRate
            }}
            scaledATokenBalance
            currentTotalDebt
          }}
        }}
        """
        try:
            aave_resp = await client.post(
                "https://api.thegraph.com/subgraphs/name/aave/protocol-v3",
                json={"query": query},
            )
            aave_data = aave_resp.json().get("data", {}).get("userReserves", [])
        except httpx.ReadTimeout:
            print("[WARN] Aave API timed out — using fallback values")
            aave_data = []
        except Exception as e:
            print(f"[WARN] Failed to parse Aave API: {e}")
            print("[DEBUG] Raw response:", getattr(aave_resp, "text", "N/A"))
            aave_data = []

        if not aave_data:
            collateral_ratio = 1.5
            leverage = 2.0
        else:
            total_collateral = sum(
                float(res.get("scaledATokenBalance", 0)) for res in aave_data
            )
            total_debt = sum(float(res.get("currentTotalDebt", 0)) for res in aave_data)
            collateral_ratio = round(
                (total_collateral / total_debt) if total_debt else 1.5, 2
            )
            leverage = round(
                1 + (total_debt / total_collateral), 2
            ) if total_collateral else 2.0

        # 4️⃣ Market trend
        market_trend = (
            round((prices[-1] - prices[0]) / prices[0], 4) if len(prices) > 1 else 0
        )

        print(
            f"[DEBUG] Data fetched: price={eth_price}, vol={volatility}, "
            f"col={collateral_ratio}, lev={leverage}"
        )

        return {
            "volatility": volatility,
            "collateral_ratio": collateral_ratio,
            "leverage": leverage,
            "asset_price": eth_price,
            "market_trend": market_trend,
        }
