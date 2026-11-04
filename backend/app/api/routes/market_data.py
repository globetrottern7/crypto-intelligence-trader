from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import MarketCandle
from app.db.session import SessionLocal

router = APIRouter(prefix="/market-data", tags=["market-data"])

STALE_AFTER_SECONDS = {
    "1m": 180,
    "5m": 600,
    "15m": 1_200,
    "1h": 4_800,
    "4h": 18_000,
    "1d": 129_600,
    "1w": 691_200,
}


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


@router.get("/status")
def market_data_status():
    """Report configured capabilities without claiming an active feed."""
    return {
        "status": "adapter_ready_provider_credentials_pending",
        "historical_rest_adapter": "implemented",
        "public_websocket_adapter": "implemented",
        "database_candle_storage": "implemented",
        "live_ingestion_running": False,
        "live_prices_available": False,
        "supported_intervals": ["1m", "5m", "15m", "1h", "4h", "1d", "1w"],
        "data_policy": {
            "timestamps": "UTC",
            "identity": "venue + symbol + interval + open_time",
            "signals_blocked_without_valid_fresh_data": True,
            "paper_only": True,
        },
    }


@router.get("/diagnostics")
def market_data_diagnostics():
    """Summarise persisted candle coverage and freshness; never infer worker health."""
    try:
        with SessionLocal() as session:
            rows = session.execute(
                select(
                    MarketCandle.venue,
                    MarketCandle.symbol,
                    MarketCandle.interval,
                    func.count(MarketCandle.id),
                    func.max(MarketCandle.close_time),
                ).where(MarketCandle.is_closed.is_(True)).group_by(
                    MarketCandle.venue, MarketCandle.symbol, MarketCandle.interval
                )
            ).all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Market data database unavailable") from exc

    now = datetime.now(UTC)
    coverage = []
    for venue, symbol, interval, candle_count, latest_close in rows:
        latest = _utc(latest_close)
        age_seconds = max(0, int((now - latest).total_seconds()))
        stale_after = STALE_AFTER_SECONDS.get(interval, 86_400)
        coverage.append({
            "venue": venue,
            "symbol": symbol,
            "interval": interval,
            "closed_candle_count": candle_count,
            "latest_close_time": latest.isoformat(),
            "age_seconds": age_seconds,
            "stale_after_seconds": stale_after,
            "fresh": age_seconds <= stale_after,
        })

    coverage.sort(key=lambda item: (item["venue"], item["symbol"], item["interval"]))
    return {
        "database_query_succeeded": True,
        "data_available": bool(coverage),
        "coverage_groups": len(coverage),
        "fresh_groups": sum(1 for item in coverage if item["fresh"]),
        "stale_groups": sum(1 for item in coverage if not item["fresh"]),
        "coverage": coverage,
        "worker_health": "not_observable_from_candle_rows",
        "live_prices_available": False,
        "paper_only": True,
    }
