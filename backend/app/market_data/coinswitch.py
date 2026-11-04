import time
from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import unquote_plus, urlencode

import httpx
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.market_data.schemas import CandleInterval, OHLCVCandle


BASE_URL = "https://coinswitch.co"
CANDLES_PATH = "/trade/api/v2/candles"
INTERVAL_MINUTES = {
    CandleInterval.M5: 5,
    CandleInterval.M15: 15,
    CandleInterval.H1: 60,
    CandleInterval.H4: 240,
    CandleInterval.D1: 1440,
    CandleInterval.W1: 10080,
}


class CoinSwitchSpotClient:
    """Read-only historical market-data client. It exposes no order methods."""

    def __init__(self, api_key: str, secret_key_hex: str, *, http_client=None, base_url=BASE_URL):
        if not api_key or not secret_key_hex:
            raise ValueError("CoinSwitch API key and secret are required")
        try:
            secret_bytes = bytes.fromhex(secret_key_hex)
        except ValueError as exc:
            raise ValueError("CoinSwitch secret must be a 32-byte hex seed") from exc
        if len(secret_bytes) != 32:
            raise ValueError("CoinSwitch secret must be a 32-byte hex seed")
        self.api_key = api_key
        self._private_key = Ed25519PrivateKey.from_private_bytes(secret_bytes)
        self.base_url = base_url.rstrip("/")
        self._http = http_client or httpx.Client(timeout=15.0)
        self._owns_http_client = http_client is None

    def close(self):
        if self._owns_http_client:
            self._http.close()

    def _signed_path(self, method, path, params, epoch_ms=None):
        query = urlencode(params)
        encoded_path = f"{path}?{query}" if query else path
        decoded_path = unquote_plus(encoded_path)
        epoch = str(epoch_ms if epoch_ms is not None else int(time.time() * 1000))
        message = f"{method.upper()}{decoded_path}{epoch}".encode()
        signature = self._private_key.sign(message).hex()
        return (
            {
                "Content-Type": "application/json",
                "X-AUTH-APIKEY": self.api_key,
                "X-AUTH-SIGNATURE": signature,
                "X-AUTH-EPOCH": epoch,
            },
            decoded_path,
        )

    def fetch_candles(
        self, *, symbol, interval, start_time_ms, end_time_ms, exchange="coinswitchx"
    ) -> list[OHLCVCandle]:
        if not symbol or "/" not in symbol:
            raise ValueError("symbol must use BASE/QUOTE format, e.g. BTC/INR")
        if start_time_ms <= 0 or end_time_ms <= start_time_ms:
            raise ValueError("invalid candle time range")
        params = {
            "exchange": exchange,
            "symbol": symbol,
            "interval": str(INTERVAL_MINUTES[interval]),
            "start_time": str(start_time_ms),
            "end_time": str(end_time_ms),
        }
        headers, signed_path = self._signed_path("GET", CANDLES_PATH, params)
        response = self._http.get(self.base_url + signed_path, headers=headers)
        response.raise_for_status()
        rows = response.json().get("data")
        if not isinstance(rows, list):
            raise TypeError("CoinSwitch candles response data must be an array")

        now = datetime.now(UTC)
        candles = []
        for row in rows:
            open_time = datetime.fromtimestamp(int(row["start_time"]) / 1000, tz=UTC)
            close_time = datetime.fromtimestamp(int(row["close_time"]) / 1000, tz=UTC)
            candles.append(
                OHLCVCandle(
                    venue=exchange,
                    symbol=row.get("symbol", symbol),
                    interval=interval,
                    open_time=open_time,
                    close_time=close_time,
                    open=Decimal(str(row["o"])),
                    high=Decimal(str(row["h"])),
                    low=Decimal(str(row["l"])),
                    close=Decimal(str(row["c"])),
                    volume=Decimal(str(row["volume"])),
                    is_closed=close_time <= now,
                )
            )
        return candles
