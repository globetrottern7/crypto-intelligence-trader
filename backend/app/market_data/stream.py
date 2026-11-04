from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import socketio

from app.market_data.schemas import CandleInterval, OHLCVCandle


SOCKET_URL = "https://ws.coinswitch.co"
SOCKET_PATH = "/pro/realtime-rates-socket/spot"
CANDLE_EVENT = "FETCH_CANDLESTICK_CS_PRO"
NAMESPACE = "/coinswitchx"


def parse_coinswitch_minute_candle(payload: dict) -> OHLCVCandle:
    """Convert the public 1-minute Socket.IO payload into a closed candle."""
    if payload.get("interval") != "1":
        raise ValueError("CoinSwitch spot stream only documents 1-minute candles")
    raw_symbol = payload.get("symbol", "")
    if "," not in raw_symbol:
        raise ValueError("WebSocket symbol must use BASE,QUOTE format")
    base, quote = raw_symbol.split(",", maxsplit=1)
    close_time = datetime.fromtimestamp(int(payload["end_time"]) / 1000, tz=UTC)
    return OHLCVCandle(
        venue="coinswitchx",
        symbol=f"{base}/{quote}",
        interval=CandleInterval.M1,
        open_time=close_time - timedelta(minutes=1),
        close_time=close_time,
        open=Decimal(str(payload["o"])),
        high=Decimal(str(payload["h"])),
        low=Decimal(str(payload["l"])),
        close=Decimal(str(payload["c"])),
        volume=Decimal(str(payload["volume"])),
        is_closed=True,
    )


class CoinSwitchCandleStream:
    """Public read-only Socket.IO candle stream with client-managed reconnects."""

    def __init__(self, symbols: list[str], on_candle: Callable[[OHLCVCandle], None], *, client=None):
        if not symbols:
            raise ValueError("at least one BASE/QUOTE symbol is required")
        if any("/" not in symbol for symbol in symbols):
            raise ValueError("symbols must use BASE/QUOTE format")
        self.symbols = symbols
        self.on_candle = on_candle
        self.client = client or socketio.Client(
            reconnection=True,
            reconnection_attempts=0,
            reconnection_delay=1,
            reconnection_delay_max=30,
            logger=False,
            engineio_logger=False,
        )
        self.client.on("connect", self._subscribe, namespace=NAMESPACE)
        self.client.on(CANDLE_EVENT, self._handle_candle, namespace=NAMESPACE)

    def _subscribe(self):
        for symbol in self.symbols:
            base, quote = symbol.split("/", maxsplit=1)
            self.client.emit(
                CANDLE_EVENT,
                {"event": "subscribe", "pair": f"{base},{quote}"},
                namespace=NAMESPACE,
            )

    def _handle_candle(self, payload):
        self.on_candle(parse_coinswitch_minute_candle(payload))

    def start(self):
        self.client.connect(
            SOCKET_URL,
            namespaces=[NAMESPACE],
            transports=["websocket"],
            socketio_path=SOCKET_PATH,
            wait=True,
            wait_timeout=30,
        )

    def stop(self):
        self.client.disconnect()
