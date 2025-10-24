# backend/mock_asi.py
from fastapi import FastAPI, Request
import random

app = FastAPI(title="Mock ASI Engine")

@app.get("/")
def root():
    return {
        "message": "🤖 Mock ASI Engine is running",
        "status": "ready",
        "endpoint": "/analyze"
    }

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()

    volatility = data.get("volatility", 0.5)
    collateral = data.get("collateral_ratio", 1.0)
    leverage = data.get("leverage", 1.0)
    asset_price = data.get("asset_price", 2000.0)
    market_trend = data.get("market_trend", 0.0)

    # Simulate an AI risk computation
    risk_score = (
        volatility * 50
        + leverage * 20
        - collateral * 10
        + (abs(market_trend) * 15)
        + random.uniform(-5, 5)
    )
    risk_score = round(max(0, min(100, risk_score)), 2)

    if risk_score < 40:
        risk_class = "🟢 Low Risk"
    elif risk_score < 70:
        risk_class = "🟡 Medium Risk"
    else:
        risk_class = "🔴 High Risk"

    return {
        "risk_probability": risk_score,
        "risk_class": risk_class,
        "message": f"Risk Score: {risk_score} — {risk_class}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
