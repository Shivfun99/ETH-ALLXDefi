# backend/app/main.py
from fastapi import FastAPI
from app.api import predict as predict_module
from .db import init_db
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.services.live_data import fetch_live_wallet_metrics 
app = FastAPI(title="OmniDeFi Risk Engine (ASI)")
from .api import predict
app.include_router(predict.router)
from app.api import wallet_risk
app.include_router(wallet_risk.router, prefix="/api", tags=["wallet"])

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()

# ✅ Mount router directly (no prefix)
app.include_router(predict_module.router)

@app.get("/health")
def health():
    return {"status": "ok", "asi_endpoint": settings.ASI_ENDPOINT}

@app.get("/")
def root():
    return {"message": "🚀 OmniDeFi Risk Engine API is running!"}
@app.get("/api/live-wallet")
def get_live_wallet(wallet: str):
    """
    Fetch real-time wallet metrics from Aave + CoinGecko.
    """
    return fetch_live_wallet_metrics(wallet)


@app.post("/api/check-wallet-risk")
def check_wallet_risk(data: dict):
    wallet = data.get("wallet")
    # Dummy logic for now
    return {
        "wallet": wallet,
        "score": 74.2,
        "category": "Moderate Risk"
    }