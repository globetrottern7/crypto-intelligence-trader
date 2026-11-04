from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    risk_per_trade: float = 0.01
    daily_loss_limit: float = 0.02
    weekly_loss_limit: float = 0.05
    max_open_positions: int = 4
    max_asset_exposure: float = 0.20


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    allowed_quantity: float
    risk_amount: float
    reason: str


def evaluate_long_entry(
    *, equity: float, price: float, stop_loss: float, requested_quantity: float,
    daily_loss_fraction: float, weekly_loss_fraction: float, open_positions: int,
    asset_exposure: float, regime: str, data_fresh: bool,
    limits: RiskLimits = RiskLimits()
) -> RiskDecision:
    if not data_fresh:
        return RiskDecision(False, 0, 0, "Market data is not fresh.")
    if equity <= 0 or price <= 0 or requested_quantity <= 0:
        return RiskDecision(False, 0, 0, "Equity, price and quantity must be positive.")
    if stop_loss <= 0 or stop_loss >= price:
        return RiskDecision(False, 0, 0, "A valid protective stop below entry is required.")
    if daily_loss_fraction >= limits.daily_loss_limit:
        return RiskDecision(False, 0, 0, "Daily loss limit reached.")
    if weekly_loss_fraction >= limits.weekly_loss_limit:
        return RiskDecision(False, 0, 0, "Weekly loss limit reached.")
    if open_positions >= limits.max_open_positions:
        return RiskDecision(False, 0, 0, "Maximum open-position count reached.")
    if regime in {"bearish", "high_volatility", "unknown"}:
        return RiskDecision(False, 0, 0, f"Market Guardian blocks entries in {regime} regime.")
    risk_budget = equity * limits.risk_per_trade
    risk_quantity = risk_budget / (price - stop_loss)
    exposure_budget = max(0.0, equity * limits.max_asset_exposure - asset_exposure)
    allowed = min(risk_quantity, exposure_budget / price)
    if allowed <= 0 or requested_quantity > allowed:
        return RiskDecision(False, allowed, risk_budget,
                            f"Requested quantity exceeds risk/exposure limit ({allowed:.8f}).")
    return RiskDecision(True, allowed, requested_quantity * (price - stop_loss),
                        "Risk checks passed; paper-only entry permitted.")
