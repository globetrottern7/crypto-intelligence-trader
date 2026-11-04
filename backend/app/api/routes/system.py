from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/system/status")
def system_status():
    return {
        "phase": "M2_market_data_foundation",
        "trading_mode": "paper_only",
        "live_execution_enabled": False,
        "modules": {
            "market_data": "contracts_and_indicators_ready_provider_pending",
            "quantitative_engine": "planned",
            "intraday_engine": "planned",
            "swing_engine": "planned",
            "paper_trading": "planned",
            "ai_mentor": "planned",
        },
    }
