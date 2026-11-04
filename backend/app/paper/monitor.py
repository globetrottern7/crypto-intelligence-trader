import time
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.db.models import MarketCandle, PaperAccount, PaperTrade
from app.db.session import SessionLocal


def run_once() -> int:
    closed = 0
    with SessionLocal() as session:
        trades = session.execute(select(PaperTrade).where(PaperTrade.status == "open")).scalars().all()
        for trade in trades:
            latest = session.execute(
                select(MarketCandle).where(
                    MarketCandle.symbol == trade.symbol, MarketCandle.interval == "1m",
                    MarketCandle.is_closed.is_(True),
                ).order_by(MarketCandle.close_time.desc()).limit(1)
            ).scalar_one_or_none()
            if latest is None:
                continue
            age = (datetime.now(UTC) - latest.close_time).total_seconds()
            if age < 0 or age > 180 or latest.close > trade.stop_loss:
                continue
            account = session.get(PaperAccount, trade.account_id)
            if account is None:
                continue
            exit_price = min(latest.close, trade.stop_loss) * (
                Decimal(1) - Decimal(str(settings.paper_slippage_bps)) / Decimal(10000)
            )
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
            closed += 1
        session.commit()
    return closed


def main() -> None:
    while True:
        run_once()
        time.sleep(15)


if __name__ == "__main__":
    main()
