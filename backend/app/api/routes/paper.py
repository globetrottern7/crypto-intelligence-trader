from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.api.schemas.paper import PaperCloseRequest, PaperOpenRequest
from app.core.config import settings
from app.db.models import MarketCandle, PaperAccount, PaperTrade
from app.db.session import SessionLocal
from app.market_data.schemas import CandleInterval, OHLCVCandle
from app.quant.analysis import analyse_candles
from app.risk.guardian import evaluate_long_entry

router = APIRouter(prefix="/paper", tags=["paper"])
ACCOUNT_ID = "primary"


def _account(session) -> PaperAccount:
    account = session.get(PaperAccount, ACCOUNT_ID)
    if account is None:
        capital = Decimal(str(settings.paper_initial_capital))
        account = PaperAccount(id=ACCOUNT_ID, initial_cash=capital, cash=capital, realised_pnl=Decimal(0))
        session.add(account)
        session.flush()
    return account


def _fresh_candles(session, symbol: str) -> list[OHLCVCandle]:
    rows = session.execute(select(MarketCandle).where(
        MarketCandle.symbol == symbol, MarketCandle.interval == CandleInterval.M1.value,
        MarketCandle.is_closed.is_(True),
    ).order_by(MarketCandle.close_time.desc()).limit(60)).scalars().all()
    candles = [
        OHLCVCandle(
            venue=row.venue, symbol=row.symbol, interval=row.interval,
            open_time=row.open_time, close_time=row.close_time,
            open=row.open, high=row.high, low=row.low, close=row.close,
            volume=row.volume, is_closed=row.is_closed,
        ) for row in reversed(rows)
    ]
    if len(candles) < 50:
        raise HTTPException(status_code=409, detail="At least 50 stored closed 1m candles are required.")
    age = (datetime.now(UTC) - candles[-1].close_time).total_seconds()
    if age < 0 or age > 180:
        raise HTTPException(status_code=409, detail="Market data is stale; paper order blocked.")
    return candles


def _loss_fractions(session, account: PaperAccount) -> tuple[float, float]:
    now = datetime.now(UTC)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = day_start - timedelta(days=day_start.weekday())
    day_pnl = session.scalar(select(func.coalesce(func.sum(PaperTrade.realised_pnl), 0)).where(
        PaperTrade.account_id == ACCOUNT_ID, PaperTrade.closed_at >= day_start
    ))
    week_pnl = session.scalar(select(func.coalesce(func.sum(PaperTrade.realised_pnl), 0)).where(
        PaperTrade.account_id == ACCOUNT_ID, PaperTrade.closed_at >= week_start
    ))
    denominator = max(float(account.initial_cash), 1.0)
    return max(0.0, -float(day_pnl or 0) / denominator), max(0.0, -float(week_pnl or 0) / denominator)


def _close_position(trade: PaperTrade, account: PaperAccount, raw_price: Decimal) -> dict:
    exit_price = raw_price * (Decimal(1) - Decimal(str(settings.paper_slippage_bps)) / Decimal(10000))
    proceeds = trade.quantity * exit_price
    exit_fee = proceeds * Decimal(str(settings.paper_fee_bps)) / Decimal(10000)
    pnl = (exit_price - trade.entry_price) * trade.quantity - trade.entry_fee - exit_fee
    account.cash += proceeds - exit_fee
    account.realised_pnl += pnl
    trade.exit_price = exit_price
    trade.exit_fee = exit_fee
    trade.realised_pnl = pnl
    trade.status = "closed"
    trade.closed_at = datetime.now(UTC)
    return {"trade_id": trade.id, "exit_price": float(exit_price), "realised_pnl": float(pnl)}


@router.get("/portfolio")
def portfolio():
    with SessionLocal() as session:
        account = _account(session)
        trades = session.execute(select(PaperTrade).where(
            PaperTrade.account_id == ACCOUNT_ID, PaperTrade.status == "open"
        ).order_by(PaperTrade.opened_at)).scalars().all()
        holdings = [{
            "trade_id": trade.id, "symbol": trade.symbol, "quantity": float(trade.quantity),
            "entry_price": float(trade.entry_price), "stop_loss": float(trade.stop_loss),
            "entry_fee": float(trade.entry_fee),
        } for trade in trades]
        market_value = sum(item["quantity"] * item["entry_price"] for item in holdings)
        result = {
            "account_id": ACCOUNT_ID, "currency": "INR",
            "initial_cash": float(account.initial_cash), "cash": float(account.cash),
            "open_positions": len(holdings), "holdings": holdings,
            "market_value_at_entry": round(market_value, 2),
            "equity_at_entry_marks": round(float(account.cash) + market_value, 2),
            "realised_pnl": float(account.realised_pnl), "execution_mode": "paper_only",
        }
        session.commit()
        return result


@router.post("/trades/open")
def open_trade(request: PaperOpenRequest):
    with SessionLocal() as session:
        account = _account(session)
        candles = _fresh_candles(session, request.symbol)
        analysis = analyse_candles(candles)
        if analysis.get("status") != "analysed" or analysis.get("recommendation") != "candidate_long":
            raise HTTPException(status_code=409, detail="Market Guardian requires a fresh confirmed long candidate.")
        price = Decimal(str(candles[-1].close)) * (
            Decimal(1) + Decimal(str(settings.paper_slippage_bps)) / Decimal(10000)
        )
        quantity = Decimal(str(request.quantity))
        stop = Decimal(str(request.stop_loss))
        opened = session.execute(select(PaperTrade).where(
            PaperTrade.account_id == ACCOUNT_ID, PaperTrade.status == "open"
        )).scalars().all()
        exposure = sum(float(item.quantity * item.entry_price) for item in opened if item.symbol == request.symbol)
        equity = float(account.cash) + sum(float(item.quantity * item.entry_price) for item in opened)
        daily_loss, weekly_loss = _loss_fractions(session, account)
        decision = evaluate_long_entry(
            equity=equity, price=float(price), stop_loss=float(stop),
            requested_quantity=float(quantity), daily_loss_fraction=daily_loss,
            weekly_loss_fraction=weekly_loss, open_positions=len(opened),
            asset_exposure=exposure, regime=analysis["regime"], data_fresh=True,
        )
        if not decision.approved:
            raise HTTPException(status_code=409, detail=decision.reason)
        notional = quantity * price
        fee = notional * Decimal(str(settings.paper_fee_bps)) / Decimal(10000)
        if notional + fee > account.cash:
            raise HTTPException(status_code=409, detail="Insufficient paper cash.")
        account.cash -= notional + fee
        trade = PaperTrade(
            account_id=ACCOUNT_ID, symbol=request.symbol, quantity=quantity,
            entry_price=price, entry_fee=fee, stop_loss=stop, status="open",
        )
        session.add(trade)
        session.commit()
        session.refresh(trade)
        return {
            "trade_id": trade.id, "status": "open", "symbol": trade.symbol,
            "quantity": float(quantity), "entry_price": float(price),
            "entry_fee": float(fee), "risk_approved": True,
            "risk_reason": decision.reason, "execution_mode": "paper_only",
        }


@router.post("/trades/close")
def close_trade(request: PaperCloseRequest):
    with SessionLocal() as session:
        trade = session.get(PaperTrade, request.trade_id)
        if trade is None or trade.account_id != ACCOUNT_ID or trade.status != "open":
            raise HTTPException(status_code=404, detail="Open paper trade not found.")
        account = _account(session)
        candles = _fresh_candles(session, trade.symbol)
        result = _close_position(trade, account, Decimal(str(candles[-1].close)))
        session.commit()
        return {**result, "status": "closed", "execution_mode": "paper_only"}


@router.post("/monitor")
def monitor_positions():
    with SessionLocal() as session:
        trades = session.execute(select(PaperTrade).where(
            PaperTrade.account_id == ACCOUNT_ID, PaperTrade.status == "open"
        )).scalars().all()
        results = []
        for trade in trades:
            latest = session.execute(select(MarketCandle).where(
                MarketCandle.symbol == trade.symbol, MarketCandle.interval == "1m",
                MarketCandle.is_closed.is_(True),
            ).order_by(MarketCandle.close_time.desc()).limit(1)).scalar_one_or_none()
            if latest is None:
                results.append({"trade_id": trade.id, "status": "no_market_data"})
                continue
            age = (datetime.now(UTC) - latest.close_time).total_seconds()
            if age < 0 or age > 180:
                results.append({"trade_id": trade.id, "status": "stale_data_no_action"})
                continue
            if latest.close <= trade.stop_loss:
                account = session.get(PaperAccount, ACCOUNT_ID)
                results.append({
                    **_close_position(trade, account, min(latest.close, trade.stop_loss)),
                    "status": "stop_loss_executed",
                })
            else:
                results.append({"trade_id": trade.id, "status": "holding"})
        session.commit()
        return {"checked": len(results), "results": results, "execution_mode": "paper_only"}


@router.get("/trades")
def trade_history(limit: int = 50):
    if not 1 <= limit <= 200:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200.")
    with SessionLocal() as session:
        rows = session.execute(select(PaperTrade).where(
            PaperTrade.account_id == ACCOUNT_ID
        ).order_by(PaperTrade.opened_at.desc()).limit(limit)).scalars().all()
        return [{
            "trade_id": row.id, "symbol": row.symbol, "quantity": float(row.quantity),
            "entry_price": float(row.entry_price),
            "exit_price": float(row.exit_price) if row.exit_price else None,
            "status": row.status,
            "realised_pnl": float(row.realised_pnl) if row.realised_pnl is not None else None,
            "opened_at": row.opened_at.isoformat(),
            "closed_at": row.closed_at.isoformat() if row.closed_at else None,
        } for row in rows]
