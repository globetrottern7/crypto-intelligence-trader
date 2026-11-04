from pydantic import BaseModel, Field

from app.market_data.schemas import OHLCVCandle


class CandleInput(OHLCVCandle):
    venue: str = "manual_backtest"


class AnalyseRequest(BaseModel):
    candles: list[CandleInput] = Field(min_length=1, max_length=5000)


class BacktestRequest(AnalyseRequest):
    fast_period: int = Field(default=10, ge=2, le=100)
    slow_period: int = Field(default=30, ge=3, le=300)
    initial_capital: float = Field(default=5000, gt=0, le=100000000)
    fee_bps: float = Field(default=10, ge=0, le=500)
    slippage_bps: float = Field(default=10, ge=0, le=500)


class ScanAsset(BaseModel):
    symbol: str = Field(min_length=3, max_length=40)
    entry_candles: list[CandleInput] = Field(min_length=1, max_length=5000)
    trend_candles: list[CandleInput] = Field(min_length=1, max_length=5000)


class ScanRequest(BaseModel):
    engine: str
    assets: list[ScanAsset] = Field(min_length=1, max_length=50)
