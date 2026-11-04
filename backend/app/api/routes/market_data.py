from fastapi import APIRouter

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/status")
def market_data_status():
    """Report readiness honestly; no provider is configured in this milestone."""
    return {
        "status": "provider_pending",
        "ingestion_enabled": False,
        "live_prices_available": False,
        "supported_intervals": ["5m", "15m", "1h", "4h", "1d", "1w"],
        "data_policy": {
            "timestamps": "UTC",
            "identity": "venue + symbol + interval",
            "signals_blocked_without_valid_fresh_data": True,
        },
    }
