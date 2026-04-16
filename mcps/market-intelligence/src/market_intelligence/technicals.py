import math

import numpy as np
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, ADXIndicator, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import MFIIndicator, OnBalanceVolumeIndicator


def _safe_float(val) -> float | None:
    try:
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 4)
    except Exception:
        return None


def _rsi_zone(rsi: float | None) -> str:
    if rsi is None:
        return "unknown"
    if rsi < 30:
        return "oversold"
    if rsi > 70:
        return "overbought"
    return "neutral"


def _mfi_zone(mfi: float | None) -> str:
    if mfi is None:
        return "unknown"
    if mfi < 20:
        return "oversold"
    if mfi > 80:
        return "overbought"
    return "neutral"


def _trend_strength(adx: float | None) -> str:
    if adx is None:
        return "unknown"
    if adx < 20:
        return "weak"
    if adx < 40:
        return "moderate"
    return "strong"


def _overall_signal(
    above_200: bool,
    above_50: bool,
    rsi: float | None,
    macd_bullish: bool,
    adx: float | None,
) -> str:
    score = 0
    if above_200:
        score += 2
    if above_50:
        score += 1
    if rsi and 45 <= rsi <= 65:
        score += 1
    if macd_bullish:
        score += 1
    if adx and adx > 25:
        score += 1

    if score >= 5:
        return "strong_bullish"
    if score >= 3:
        return "bullish"
    if score >= 2:
        return "neutral"
    if score == 1:
        return "bearish"
    return "strong_bearish"


def _pivot_position(price: float, pivot: float, r1: float, s1: float) -> str:
    """Describe where the current price sits relative to pivot levels."""
    if price > r1:
        return "above R1 — bullish, approaching resistance"
    if price > pivot:
        return "between pivot and R1 — mild bullish bias"
    if price > s1:
        return "between S1 and pivot — mild bearish bias"
    return "below S1 — bearish, approaching support"


def _52w_signal(proximity_pct: float) -> str:
    """Signal based on proximity to 52-week high (George & Hwang momentum factor)."""
    if proximity_pct >= 0:
        return "at_or_above_52w_high"
    if proximity_pct >= -5:
        return "near_52w_high"
    if proximity_pct >= -15:
        return "moderate_momentum"
    if proximity_pct >= -30:
        return "weak_momentum"
    return "far_from_high"


def get_technicals_impl(symbol: str, period: str = "1y") -> dict:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        info = ticker.info or {}
    except Exception as e:
        return {"symbol": symbol, "error": f"Failed to fetch history: {e}"}

    if df is None or len(df) < 50:
        return {
            "symbol": symbol,
            "error": f"Insufficient data: only {len(df) if df is not None else 0} data points (need 50+).",
        }

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    current_price = _safe_float(close.iloc[-1])

    # SMA 50 and 200
    sma50_series = SMAIndicator(close, window=50).sma_indicator()
    sma200_series = SMAIndicator(close, window=200).sma_indicator() if len(df) >= 200 else None

    sma50 = _safe_float(sma50_series.iloc[-1])
    sma200 = _safe_float(sma200_series.iloc[-1]) if sma200_series is not None else None

    above_50 = bool(current_price and sma50 and current_price > sma50)
    above_200 = bool(current_price and sma200 and current_price > sma200)

    price_vs_200_pct = None
    if current_price and sma200:
        price_vs_200_pct = round((current_price - sma200) / sma200 * 100, 2)

    # Golden/Death cross — compare last two SMA50 vs SMA200 crossovers
    golden_cross = False
    death_cross = False
    if sma200_series is not None and len(sma50_series.dropna()) >= 2 and len(sma200_series.dropna()) >= 2:
        prev_50 = _safe_float(sma50_series.iloc[-2])
        prev_200 = _safe_float(sma200_series.iloc[-2])
        if prev_50 and prev_200 and sma50 and sma200:
            if prev_50 <= prev_200 and sma50 > sma200:
                golden_cross = True
            elif prev_50 >= prev_200 and sma50 < sma200:
                death_cross = True

    # RSI
    rsi_series = RSIIndicator(close, window=14).rsi()
    rsi = _safe_float(rsi_series.iloc[-1])

    # MACD
    macd_obj = MACD(close)
    macd_line = _safe_float(macd_obj.macd().iloc[-1])
    macd_signal = _safe_float(macd_obj.macd_signal().iloc[-1])
    macd_hist = _safe_float(macd_obj.macd_diff().iloc[-1])
    macd_bullish = bool(macd_line and macd_signal and macd_line > macd_signal)

    # ATR
    atr_obj = AverageTrueRange(high, low, close, window=14)
    atr = _safe_float(atr_obj.average_true_range().iloc[-1])
    atr_pct = round(atr / current_price * 100, 2) if atr and current_price else None

    # Bollinger Bands
    bb = BollingerBands(close, window=20, window_dev=2)
    bb_upper = _safe_float(bb.bollinger_hband().iloc[-1])
    bb_mid = _safe_float(bb.bollinger_mavg().iloc[-1])
    bb_lower = _safe_float(bb.bollinger_lband().iloc[-1])
    bb_pct_b = _safe_float(bb.bollinger_pband().iloc[-1])
    bb_width = _safe_float(bb.bollinger_wband().iloc[-1])

    # ADX
    adx_obj = ADXIndicator(high, low, close, window=14)
    adx = _safe_float(adx_obj.adx().iloc[-1])
    plus_di = _safe_float(adx_obj.adx_pos().iloc[-1])
    minus_di = _safe_float(adx_obj.adx_neg().iloc[-1])
    trend_direction = "bullish" if (plus_di and minus_di and plus_di > minus_di) else "bearish"

    # MFI
    mfi_series = MFIIndicator(high, low, close, volume, window=14).money_flow_index()
    mfi = _safe_float(mfi_series.iloc[-1])

    # OBV
    obv_series = OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    obv_current = _safe_float(obv_series.iloc[-1])
    obv_5d_ago = _safe_float(obv_series.iloc[-6]) if len(obv_series) >= 6 else None
    obv_trend = None
    if obv_current is not None and obv_5d_ago is not None:
        obv_trend = "rising" if obv_current > obv_5d_ago else "falling"

    # Volume vs 20-day avg
    avg_vol_20 = _safe_float(volume.rolling(20).mean().iloc[-1])
    current_vol = _safe_float(volume.iloc[-1])
    vol_vs_avg = round(current_vol / avg_vol_20, 2) if current_vol and avg_vol_20 else None

    # Stop loss suggestion
    stop_loss = round(current_price - 2 * atr, 4) if current_price and atr else None

    overall = _overall_signal(above_200, above_50, rsi, macd_bullish, adx)

    # --- Support & Resistance (Classic Pivot Points) ---
    # Use last 5 days of data for recent OHLC pivot calculation
    support_resistance = None
    try:
        recent = df.tail(5)
        ph = _safe_float(recent["High"].max())
        pl = _safe_float(recent["Low"].min())
        pc = _safe_float(recent["Close"].iloc[-1])
        if ph and pl and pc:
            pivot = round((ph + pl + pc) / 3, 4)
            r1 = round(2 * pivot - pl, 4)
            r2 = round(pivot + (ph - pl), 4)
            r3 = round(ph + 2 * (pivot - pl), 4)
            s1 = round(2 * pivot - ph, 4)
            s2 = round(pivot - (ph - pl), 4)
            s3 = round(pl - 2 * (ph - pivot), 4)
            bias = "bullish" if (current_price and current_price > pivot) else "bearish"
            position = _pivot_position(current_price, pivot, r1, s1) if current_price else "unknown"
            support_resistance = {
                "pivot": pivot,
                "resistance": {"R1": r1, "R2": r2, "R3": r3},
                "support": {"S1": s1, "S2": s2, "S3": s3},
                "current_price": current_price,
                "position": position,
                "bias": bias,
                "note": "Levels based on 5-day OHLC pivot. Price above pivot = bullish bias.",
            }
    except Exception:
        support_resistance = {"error": "Could not compute pivot levels"}

    # --- 52-Week High Momentum Factor (George & Hwang, 2004) ---
    momentum_factor = None
    try:
        high_52w = info.get("fiftyTwoWeekHigh")
        low_52w = info.get("fiftyTwoWeekLow")
        if high_52w and current_price:
            proximity_pct = round((current_price - high_52w) / high_52w * 100, 2)
            from_low_pct = round((current_price - low_52w) / low_52w * 100, 2) if low_52w else None
            signal = _52w_signal(proximity_pct)
            momentum_factor = {
                "52w_high": _safe_float(high_52w),
                "52w_low": _safe_float(low_52w),
                "current_price": current_price,
                "proximity_to_high_pct": proximity_pct,
                "from_low_pct": from_low_pct,
                "signal": signal,
                "note": (
                    "BREAKOUT: At/above 52W high — historically strong buy signal" if signal == "at_or_above_52w_high"
                    else "NEAR HIGH: Within 5% of 52W high — bullish momentum factor" if signal == "near_52w_high"
                    else "MODERATE: 5-15% from 52W high — recovering" if signal == "moderate_momentum"
                    else "WEAK: 15-30% from 52W high — limited momentum" if signal == "weak_momentum"
                    else "FAR: >30% below 52W high — no momentum factor"
                ),
            }
    except Exception:
        momentum_factor = {"error": "Could not compute 52W high momentum"}

    return {
        "symbol": symbol,
        "period": period,
        "data_points": len(df),
        "trend": {
            "sma_50": sma50,
            "sma_200": sma200,
            "above_50dma": above_50,
            "above_200dma": above_200,
            "golden_cross": golden_cross,
            "death_cross": death_cross,
            "price_vs_200dma_pct": price_vs_200_pct,
        },
        "momentum": {
            "rsi_14": rsi,
            "rsi_zone": _rsi_zone(rsi),
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_histogram": macd_hist,
            "macd_bullish": macd_bullish,
        },
        "volatility": {
            "atr_14": atr,
            "atr_pct": atr_pct,
            "bb_upper": bb_upper,
            "bb_mid": bb_mid,
            "bb_lower": bb_lower,
            "bb_pct_b": bb_pct_b,
            "bb_width": bb_width,
        },
        "strength": {
            "adx_14": adx,
            "plus_di": plus_di,
            "minus_di": minus_di,
            "trend_strength": _trend_strength(adx),
            "trend_direction": trend_direction,
        },
        "volume": {
            "mfi_14": mfi,
            "mfi_zone": _mfi_zone(mfi),
            "obv_current": obv_current,
            "obv_5d_ago": obv_5d_ago,
            "obv_trend": obv_trend,
            "volume_vs_avg_20d": vol_vs_avg,
        },
        "signals": {
            "overall": overall,
            "suggested_stop_loss": stop_loss,
            "current_price": current_price,
        },
        "support_resistance": support_resistance,
        "momentum_factor": momentum_factor,
    }
