from fastapi import APIRouter

router = APIRouter(prefix="/market-data", tags=["market-data"])


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
