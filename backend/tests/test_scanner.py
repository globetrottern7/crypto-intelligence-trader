from app.quant.scanner import scan_assets


def test_scanner_rejects_unknown_engine():
    try:
        scan_assets([], engine="unknown")
    except ValueError as exc:
        assert "intraday or swing" in str(exc)
    else:
        raise AssertionError("Unknown engine should be rejected")


def test_scanner_returns_zero_candidates_when_no_assets():
    result = scan_assets([], engine="intraday")
    assert result["candidate_count"] == 0
    assert result["no_trade_is_valid"] is True
