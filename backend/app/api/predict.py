from fastapi import APIRouter, HTTPException
from ..schemas import RiskInput, RiskOutput
from ..services.risk_model import predict
from ..db import SessionLocal, Prediction
import datetime
import requests

# Router with prefix `/api`
router = APIRouter(prefix="/api", tags=["Risk Prediction"])


# --- 🟢 Market Data Fetcher (Dynamic Asset) ---
def fetch_market_data(asset_symbol: str):
    """
    Fetch live asset price (USD) and 24h trend % from CoinGecko for a given symbol.
    Falls back gracefully if unavailable.
    """
    symbol_map = {
        "eth": "ethereum",
        "btc": "bitcoin",
        "uni": "uniswap",
        "aave": "aave",
        "usdc": "usd-coin",
        "sol": "solana",
    }

    asset_id = symbol_map.get(asset_symbol.lower(), asset_symbol.lower())
    try:
        # ✅ Price
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd"
        res = requests.get(url, timeout=5).json()
        price = res[asset_id]["usd"]

        # ✅ Trend (24h %)
        trend_url = f"https://api.coingecko.com/api/v3/coins/{asset_id}"
        trend_data = requests.get(trend_url, timeout=5).json()
        market_trend = trend_data["market_data"]["price_change_percentage_24h"] / 100

        print(f"[MARKET] {asset_symbol.upper()} → ${price:.2f}, trend={market_trend:.4f}")
        return price, market_trend
    except Exception as e:
        print(f"[WARN] Market fetch failed for {asset_symbol}: {e}")
        return 2000.0, 0.0  # fallback defaults


# ✅ FINAL ENDPOINT (matches frontend)
@router.post("/predict-risk", response_model=RiskOutput)
async def predict_endpoint(payload: RiskInput):
    features = payload.dict(exclude_none=True)

    # 🧠 Auto-fetch live market data if not provided
    asset_symbol = features.get("asset_symbol", "eth")
    if not features.get("asset_price") or not features.get("market_trend"):
        price, trend = fetch_market_data(asset_symbol)
        features["asset_price"] = features.get("asset_price", price)
        features["market_trend"] = features.get("market_trend", trend)

    # 🔮 Run the Risk Model (connected to ASI)
    result = await predict(features)

    # 💾 Save to DB (optional best-effort)
    try:
        db = SessionLocal()
        rec = Prediction(
            timestamp=datetime.datetime.utcnow(),
            input=features,
            output=result,
            protocol=features.get("protocol"),
            user_wallet=features.get("user_wallet"),
        )
        db.add(rec)
        db.commit()
    except Exception as e:
        print(f"[DB WARN] Could not save prediction: {e}")
    finally:
        try:
            db.close()
        except Exception:
            pass

    # 🧩 Validate ASI response
    if "risk_probability" not in result:
        raise HTTPException(status_code=502, detail="ASI returned unexpected response")

    return {
        "risk_probability": float(result.get("risk_probability", 0.0)),
        "risk_class": result.get("risk_class", "Unknown"),
        "action": result.get("action", ""),
        "explanation": result.get("explanation", ""),
    }
