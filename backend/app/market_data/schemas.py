from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CandleInterval(StrEnum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class OHLCVCandle(BaseModel):
    """A single venue-specific OHLCV candle; timestamps are normalised to UTC."""

    model_config = ConfigDict(frozen=True)

    venue: str = Field(min_length=1, max_length=40)
    symbol: str = Field(min_length=3, max_length=40)
    interval: CandleInterval
    open_time: datetime
    close_time: datetime
    open: Decimal = Field(gt=0)
    high: Decimal = Field(gt=0)
    low: Decimal = Field(gt=0)
    close: Decimal = Field(gt=0)
    volume: Decimal = Field(ge=0)
    is_closed: bool

    @field_validator("open_time", "close_time")
    @classmethod
    def require_timezone_and_normalise(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Candle timestamps must include a timezone")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_ohlc(self):
        if self.close_time <= self.open_time:
            raise ValueError("close_time must be after open_time")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be the greatest OHLC value")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be the smallest OHLC value")
        return self
