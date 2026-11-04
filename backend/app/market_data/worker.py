import os

from app.db.session import SessionLocal
from app.market_data.service import MarketDataIngestionService
from app.market_data.stream import CoinSwitchCandleStream


def main():
    symbols = [
        item.strip()
        for item in os.getenv("MARKET_DATA_SYMBOLS", "BTC/INR").split(",")
        if item.strip()
    ]
    service = MarketDataIngestionService(SessionLocal)
    stream = CoinSwitchCandleStream(symbols, service.handle)
    try:
        stream.start()
        stream.client.wait()
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()


if __name__ == "__main__":
    main()
