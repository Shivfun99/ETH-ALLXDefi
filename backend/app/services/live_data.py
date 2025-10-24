import requests

def fetch_live_wallet_metrics(wallet: str):
    """
    Fetch live DeFi wallet metrics from Aave and CoinGecko.
    Falls back to mock data if wallet not found or API fails.
    """
    try:
        # ✅ 1. Get ETH price
        cg = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        ).json()
        eth_price = cg["ethereum"]["usd"]

        # ✅ 2. Query Aave subgraph
        query = f"""
        {{
          users(where: {{id: "{wallet.lower()}"}}) {{
            totalCollateralETH
            totalBorrowsETH
          }}
        }}
        """

        resp = requests.post(
            "https://api.thegraph.com/subgraphs/name/aave/protocol-v2",
            json={"query": query},
        ).json()

        users = resp.get("data", {}).get("users", [])
        if not users:
            return {
                "volatility": 0.5,
                "collateral_ratio": 1.0,
                "leverage": 1.5,
                "eth_price": eth_price,
                "source": "mock",
            }

        user = users[0]
        collateral = float(user["totalCollateralETH"])
        borrows = float(user["totalBorrowsETH"])

        collateral_ratio = collateral / max(borrows, 0.0001)
        leverage = 1 + (borrows / max(collateral, 0.0001))

        return {
            "volatility": 0.4,
            "collateral_ratio": round(collateral_ratio, 2),
            "leverage": round(leverage, 2),
            "eth_price": eth_price,
            "source": "live",
        }

    except Exception as e:
        print("❌ Error fetching live DeFi data:", e)
        return {
            "volatility": 0.6,
            "collateral_ratio": 1.1,
            "leverage": 2.0,
            "eth_price": 2000,
            "source": "fallback",
        } 