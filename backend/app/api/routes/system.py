from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/system/status")
def system_status():
    return {
        "phase": "P0",
        "trading_mode": "paper_only",
        "live_execution_enabled": False,
        "modules": {
            "market_data": "planned",
            "quantitative_engine": "planned",
            "intraday_engine": "planned",
            "swing_engine": "planned",
            "paper_trading": "planned",
            "ai_mentor": "planned",
        },
    }
