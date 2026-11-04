from collections.abc import Sequence


def ema(values: Sequence[float], period: int) -> list[float | None]:
    if period < 1:
        raise ValueError("period must be positive")
    result: list[float | None] = [None] * len(values)
    if len(values) < period:
        return result
    current = sum(values[:period]) / period
    result[period - 1] = current
    multiplier = 2 / (period + 1)
    for index in range(period, len(values)):
        current = (values[index] - current) * multiplier + current
        result[index] = current
    return result


def sma(values: Sequence[float], period: int) -> list[float | None]:
    if period < 1:
        raise ValueError("period must be positive")
    result: list[float | None] = [None] * len(values)
    for index in range(period - 1, len(values)):
        result[index] = sum(values[index - period + 1:index + 1]) / period
    return result


def rsi(values: Sequence[float], period: int = 14) -> list[float | None]:
    if period < 1:
        raise ValueError("period must be positive")
    result: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return result
    changes = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(change, 0.0) for change in changes]
    losses = [max(-change, 0.0) for change in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    def value(gain: float, loss: float) -> float:
        if loss == 0:
            return 100.0 if gain > 0 else 50.0
        return 100 - 100 / (1 + gain / loss)

    result[period] = value(avg_gain, avg_loss)
    for index in range(period + 1, len(values)):
        change_index = index - 1
        avg_gain = (avg_gain * (period - 1) + gains[change_index]) / period
        avg_loss = (avg_loss * (period - 1) + losses[change_index]) / period
        result[index] = value(avg_gain, avg_loss)
    return result


def macd(values: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9):
    if fast >= slow:
        raise ValueError("fast period must be smaller than slow period")
    fast_line = ema(values, fast)
    slow_line = ema(values, slow)
    line = [a - b if a is not None and b is not None else None
            for a, b in zip(fast_line, slow_line, strict=True)]
    valid = [value for value in line if value is not None]
    signal_valid = ema(valid, signal)
    signal_line: list[float | None] = [None] * len(values)
    cursor = 0
    for index, value in enumerate(line):
        if value is not None:
            signal_line[index] = signal_valid[cursor]
            cursor += 1
    histogram = [a - b if a is not None and b is not None else None
                 for a, b in zip(line, signal_line, strict=True)]
    return line, signal_line, histogram


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14):
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("OHLC arrays must have equal lengths")
    if period < 1:
        raise ValueError("period must be positive")
    ranges = []
    for index, (high, low) in enumerate(zip(highs, lows, strict=True)):
        previous_close = closes[index - 1] if index else closes[index]
        ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    result: list[float | None] = [None] * len(ranges)
    if len(ranges) < period:
        return result
    current = sum(ranges[:period]) / period
    result[period - 1] = current
    for index in range(period, len(ranges)):
        current = (current * (period - 1) + ranges[index]) / period
        result[index] = current
    return result


def vwap(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], volumes: Sequence[float]):
    if not (len(highs) == len(lows) == len(closes) == len(volumes)):
        raise ValueError("OHLCV arrays must have equal lengths")
    cumulative_value = 0.0
    cumulative_volume = 0.0
    result = []
    for high, low, close, volume in zip(highs, lows, closes, volumes, strict=True):
        typical = (high + low + close) / 3
        cumulative_value += typical * volume
        cumulative_volume += volume
        result.append(cumulative_value / cumulative_volume if cumulative_volume else None)
    return result
