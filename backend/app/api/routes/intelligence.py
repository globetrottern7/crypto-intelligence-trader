from fastapi import APIRouter, HTTPException

from app.api.schemas.intelligence import AnalyseRequest, BacktestRequest, ScanRequest
from app.market_data.schemas import OHLCVCandle
from app.mentor.explainer import explain_analysis
from app.quant.analysis import analyse_candles
from app.quant.backtesting import run_sma_crossover_backtest
from app.quant.scanner import scan_assets

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def _candles(items):
    return [OHLCVCandle.model_validate(item.model_dump()) for item in items]


@router.post("/analyse")
def analyse(request: AnalyseRequest):
    candles = _candles(request.candles)
    if len({item.symbol for item in candles}) != 1:
        raise HTTPException(status_code=422, detail="Analyse one symbol at a time.")
    result = analyse_candles(candles)
    result["symbol"] = candles[0].symbol
    result["explanation"] = explain_analysis(result)
    return result


@router.post("/scan")
def scan(request: ScanRequest):
    assets = [{
        "symbol": asset.symbol,
        "entry_candles": _candles(asset.entry_candles),
        "trend_candles": _candles(asset.trend_candles),
    } for asset in request.assets]
    try:
        return scan_assets(assets, engine=request.engine)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/backtest")
def backtest(request: BacktestRequest):
    if request.fast_period >= request.slow_period:
        raise HTTPException(status_code=422, detail="fast_period must be below slow_period.")
    candles = _candles(request.candles)
    if len({item.symbol for item in candles}) != 1:
        raise HTTPException(status_code=422, detail="Backtest one symbol at a time.")
    try:
        result = run_sma_crossover_backtest(
            candles, fast_period=request.fast_period, slow_period=request.slow_period,
            initial_capital=request.initial_capital, fee_bps=request.fee_bps,
            slippage_bps=request.slippage_bps,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result["symbol"] = candles[0].symbol
    return result
