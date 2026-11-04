from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/system/status")
def system_status():
    return {
        "phase": "M3_to_M10_paper_trading_foundation",
        "trading_mode": "paper_only",
        "live_execution_enabled": False,
        "modules": {
            "market_data": "adapter_and_ingestion_implemented_runtime_pending",
            "quantitative_engine": "indicators_regime_and_analysis_implemented",
            "intraday_engine": "5m_entry_15m_confirmation_scanner_implemented",
            "swing_engine": "4h_entry_1d_confirmation_scanner_implemented",
            "backtesting": "sma_crossover_with_fee_and_slippage_model_implemented",
            "paper_trading": "persistent_long_only_ledger_implemented",
            "risk_guardian": "deterministic_entry_controls_implemented",
            "ai_mentor": "deterministic_explainer_implemented_llm_optional",
            "android_dashboard": "responsive_pwa_shell_implemented",
            "cloud_runtime": "container_and_ci_cd_assets_implemented_deployment_pending",
        },
    }
