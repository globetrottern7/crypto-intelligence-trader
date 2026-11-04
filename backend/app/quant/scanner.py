from collections.abc import Sequence

from app.market_data.schemas import CandleInterval, OHLCVCandle
from app.mentor.explainer import explain_analysis
from app.quant.analysis import analyse_candles

ENGINE_INTERVALS = {
    "intraday": (CandleInterval.M5, CandleInterval.M15),
    "swing": (CandleInterval.H4, CandleInterval.D1),
}


def scan_assets(assets: Sequence[dict], *, engine: str, max_assets: int = 50) -> dict:
    if engine not in ENGINE_INTERVALS:
        raise ValueError("engine must be intraday or swing")
    if len(assets) > max_assets:
        raise ValueError(f"At most {max_assets} assets may be scanned per request")
    entry_interval, trend_interval = ENGINE_INTERVALS[engine]
    results = []
    for asset in assets:
        entry: list[OHLCVCandle] = asset["entry_candles"]
        trend: list[OHLCVCandle] = asset["trend_candles"]
        symbol = asset["symbol"]
        if any(item.symbol != symbol for item in [*entry, *trend]):
            results.append({"symbol": symbol, "recommendation": "no_trade", "reason": "Candle symbol mismatch."})
            continue
        if any(item.interval != entry_interval for item in entry) or any(item.interval != trend_interval for item in trend):
            results.append({"symbol": symbol, "recommendation": "no_trade",
                            "reason": f"{engine} requires {entry_interval.value} entry and {trend_interval.value} trend candles."})
            continue
        entry_result = analyse_candles(entry)
        trend_result = analyse_candles(trend)
        aligned = entry_result.get("recommendation") == "candidate_long" and trend_result.get("regime") == "bullish"
        recommendation = "candidate_long" if aligned else "no_trade"
        reasons = [
            f"Entry timeframe: {entry_result.get('reason') or entry_result.get('recommendation')}.",
            f"Confirmation timeframe: {trend_result.get('reason') or trend_result.get('regime', 'unavailable')}.",
        ]
        if not aligned:
            reasons.append("Both timeframes must independently confirm a fresh bullish setup.")
        result = {
            "symbol": symbol, "engine": engine, "recommendation": recommendation,
            "entry_analysis": entry_result, "trend_analysis": trend_result,
            "reasons": reasons, "paper_only": True,
        }
        result["explanation"] = explain_analysis({"recommendation": recommendation, "reasons": reasons})
        results.append(result)
    results.sort(key=lambda item: item.get("entry_analysis", {}).get("score", -999), reverse=True)
    return {
        "engine": engine, "assets_scanned": len(results),
        "candidate_count": sum(1 for item in results if item["recommendation"] == "candidate_long"),
        "results": results, "no_trade_is_valid": True,
    }
