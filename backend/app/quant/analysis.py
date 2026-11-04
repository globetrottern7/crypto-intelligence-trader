from collections.abc import Sequence
from datetime import UTC, datetime

from app.market_data.schemas import OHLCVCandle
from app.quant.indicators import atr, ema, macd, rsi, vwap

STALE_AFTER_SECONDS = {
    "1m": 180, "5m": 600, "15m": 1_200, "1h": 4_800,
    "4h": 18_000, "1d": 129_600, "1w": 691_200,
}


def analyse_candles(candles: Sequence[OHLCVCandle], *, minimum_bars: int = 50, data_fresh: bool = True) -> dict:
    if len(candles) < minimum_bars:
        return {"status": "insufficient_data", "recommendation": "no_trade",
                "reason": f"At least {minimum_bars} closed candles are required.", "bars": len(candles)}
    ordered = sorted(candles, key=lambda item: item.open_time)
    if any(not candle.is_closed for candle in ordered):
        return {"status": "invalid_data", "recommendation": "no_trade",
                "reason": "Open candles are not eligible for analysis."}
    closes = [float(item.close) for item in ordered]
    highs = [float(item.high) for item in ordered]
    lows = [float(item.low) for item in ordered]
    volumes = [float(item.volume) for item in ordered]
    fast = ema(closes, 20)[-1]
    slow = ema(closes, 50)[-1]
    momentum = rsi(closes, 14)[-1]
    macd_line, signal_line, histogram = macd(closes)
    volatility = atr(highs, lows, closes, 14)[-1]
    volume_weighted = vwap(highs, lows, closes, volumes)[-1]
    latest = ordered[-1]
    raw_age = (datetime.now(UTC) - latest.close_time).total_seconds()
    age_seconds = int(raw_age)
    stale_after = STALE_AFTER_SECONDS.get(latest.interval.value, 180)
    if not data_fresh or raw_age < 0 or raw_age > stale_after:
        return {"status": "stale_data", "recommendation": "no_trade",
                "reason": "Latest candle is stale or freshness has not been verified.",
                "latest_close_time": latest.close_time.isoformat(), "age_seconds": age_seconds}
    if any(value is None for value in (fast, slow, momentum, histogram[-1], volatility)):
        return {"status": "insufficient_indicator_history", "recommendation": "no_trade"}
    score = 0
    reasons = []
    if fast > slow:
        score += 25
        reasons.append("EMA 20 is above EMA 50.")
    else:
        score -= 25
        reasons.append("EMA 20 is below EMA 50.")
    if momentum >= 55:
        score += 20
        reasons.append("RSI momentum is positive.")
    elif momentum <= 45:
        score -= 20
        reasons.append("RSI momentum is negative.")
    else:
        reasons.append("RSI is in a neutral band.")
    if histogram[-1] > 0:
        score += 15
        reasons.append("MACD histogram is positive.")
    else:
        score -= 15
        reasons.append("MACD histogram is negative.")
    if volume_weighted is not None and closes[-1] >= volume_weighted:
        score += 10
        reasons.append("Price is at or above cumulative VWAP.")
    elif volume_weighted is not None:
        score -= 10
        reasons.append("Price is below cumulative VWAP.")
    atr_pct = volatility / closes[-1] * 100 if closes[-1] else 0
    if atr_pct > 5:
        regime = "high_volatility"
    elif fast > slow and score >= 25:
        regime = "bullish"
    elif fast < slow and score <= -25:
        regime = "bearish"
    else:
        regime = "sideways"
    recommendation = "watch"
    if score >= 45 and regime == "bullish":
        recommendation = "candidate_long"
    elif score <= -45 and regime == "bearish":
        recommendation = "avoid_long"
    if regime == "high_volatility":
        recommendation = "no_trade"
        reasons.append("Volatility guard overrides directional scoring.")
    return {
        "status": "analysed", "recommendation": recommendation, "score": score, "regime": regime,
        "indicators": {
            "ema_20": round(fast, 8), "ema_50": round(slow, 8),
            "rsi_14": round(momentum, 4), "macd": round(macd_line[-1], 8),
            "macd_signal": round(signal_line[-1], 8),
            "macd_histogram": round(histogram[-1], 8),
            "atr_14": round(volatility, 8), "atr_percent": round(atr_pct, 4),
            "vwap": round(volume_weighted, 8) if volume_weighted is not None else None,
        },
        "reasons": reasons, "latest_close_time": latest.close_time.isoformat(),
        "data_fresh": True, "paper_only": True,
    }
