from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RiskInput(BaseModel):
    volatility: float = Field(..., description="Estimated volatility (0-1)")
    collateral_ratio: float = Field(..., description="Collateral ratio, e.g., 1.2")
    leverage: float = Field(..., description="Leverage factor, e.g., 2.5")
    asset_price: float = Field(..., description="Current asset price in USD")
    market_trend: float = Field(..., description="Market trend (e.g. -0.1 for -10%)")
    protocol: Optional[str] = Field("Aave", description="Protocol name")
    user_wallet: Optional[str] = Field(None, description="User wallet address")
    timestamp: Optional[datetime] = None

class RiskOutput(BaseModel):
    risk_probability: float
    risk_class: str
    action: str
    explanation: Optional[str] = None
