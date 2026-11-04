from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.market_data.coinswitch import CoinSwitchSpotClient
from app.market_data.schemas import CandleInterval


def test_signing_matches_ed25519_message_contract():
    seed = bytes(range(32))
    client = CoinSwitchSpotClient("public-key-hex", seed.hex(), http_client=httpx.Client())
    headers, path = client._signed_path(
        "GET",
        "/trade/api/v2/candles",
        {"symbol": "BTC/INR", "interval": "5"},
        epoch_ms=1719905777483,
    )
    message = f"GET{path}1719905777483".encode()
    public_key = Ed25519PrivateKey.from_private_bytes(seed).public_key()
    public_key.verify(bytes.fromhex(headers["X-AUTH-SIGNATURE"]), message)
    assert path == "/trade/api/v2/candles?symbol=BTC/INR&interval=5"
    client.close()


def test_fetch_candles_normalises_provider_payload():
    seed = bytes(range(32))
    response = httpx.Response(
        200,
        json={
            "data": [{
                "o": "100.25", "h": "105", "l": "99", "c": "103",
                "volume": "2.5", "symbol": "BTC/INR", "interval": "5",
                "start_time": "1798761600000", "close_time": "1798761900000",
            }]
        },
        request=httpx.Request("GET", "https://coinswitch.co"),
    )
    transport = httpx.MockTransport(lambda request: response)
    http = httpx.Client(transport=transport)
    client = CoinSwitchSpotClient("public-key-hex", seed.hex(), http_client=http)
    candles = client.fetch_candles(
        symbol="BTC/INR",
        interval=CandleInterval.M5,
        start_time_ms=1798761600000,
        end_time_ms=1798761900000,
    )
    assert len(candles) == 1
    assert candles[0].venue == "coinswitchx"
    assert candles[0].open == Decimal("100.25")
    assert candles[0].open_time.tzinfo == UTC
    client.close()


def test_client_rejects_missing_or_malformed_credentials():
    with pytest.raises(ValueError):
        CoinSwitchSpotClient("", "00" * 32)
    with pytest.raises(ValueError):
        CoinSwitchSpotClient("key", "not-hex")
    with pytest.raises(ValueError):
        CoinSwitchSpotClient("key", "00" * 16)
