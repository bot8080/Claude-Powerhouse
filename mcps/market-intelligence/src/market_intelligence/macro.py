import math

import yfinance as yf


def _safe_float(val) -> float | None:
    try:
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 4)
    except Exception:
        return None


def _vix_zone(vix: float | None) -> tuple[str, str]:
    """Return (zone_label, signal) for VIX level."""
    if vix is None:
        return "unknown", "⚪"
    if vix < 15:
        return "complacency", "🟢"
    if vix < 20:
        return "calm", "🟢"
    if vix < 30:
        return "elevated_fear", "🟡"
    if vix < 40:
        return "high_fear", "🔴"
    return "crisis", "⛔"


def _yield_curve_zone(spread: float | None) -> tuple[str, str]:
    """Return (shape, signal) for 10Y - 3M yield spread."""
    if spread is None:
        return "unknown", "⚪"
    if spread > 1.0:
        return "steep_normal", "🟢"
    if spread > 0:
        return "flattening", "🟡"
    return "inverted", "🔴"


def _dxy_trend(change_pct: float | None) -> str:
    """Interpret DXY direction for equity context."""
    if change_pct is None:
        return "unknown"
    if change_pct > 1.0:
        return "rising_strongly \u2014 headwind for US multinational earnings"
    if change_pct > 0.3:
        return "rising_mildly \u2014 slight headwind"
    if change_pct < -1.0:
        return "falling_strongly \u2014 tailwind for commodities and emerging markets"
    if change_pct < -0.3:
        return "falling_mildly \u2014 slight tailwind"
    return "stable \u2014 neutral impact"


def _macro_summary(vix_zone: str, curve_shape: str) -> str:
    """Produce a single-line macro sentiment summary."""
    if vix_zone == "crisis":
        return "⛔ MARKET CRISIS \u2014 capital preservation mode, avoid new positions"
    if vix_zone == "high_fear" and curve_shape == "inverted":
        return "🔴 HIGH RISK \u2014 fear elevated + inverted curve: maximum caution"
    if vix_zone in ("high_fear", "elevated_fear") and curve_shape == "inverted":
        return "🔴 DEFENSIVE \u2014 recessionary signals present, prefer quality/defensive sectors"
    if curve_shape == "inverted":
        return "🟡 CAUTION \u2014 inverted yield curve (recession historically follows 12-18 months)"
    if vix_zone in ("high_fear", "elevated_fear"):
        return "🟡 SELECTIVE \u2014 elevated fear, prefer high-quality names with strong balance sheets"
    if vix_zone in ("complacency", "calm") and curve_shape in ("steep_normal", "flattening"):
        return "🟢 FAVOURABLE \u2014 calm market, yield curve healthy, risk-on environment"
    return "🟡 NEUTRAL \u2014 mixed macro signals, stock-specific analysis most important"


def get_us_macro_impl() -> dict:
    """Fetch US macro indicators: VIX (fear gauge), Yield Curve (10Y-3M), and DXY (US Dollar).
    All data via yfinance. No external APIs required.
    """
    result: dict = {"market": "US Macro Overlay"}

    # --- VIX (Fear Gauge) ---
    try:
        vix_ticker = yf.Ticker("^VIX")
        vix_hist = vix_ticker.history(period="5d")
        vix_val = _safe_float(vix_hist["Close"].iloc[-1]) if not vix_hist.empty else None
        vix_prev = _safe_float(vix_hist["Close"].iloc[-2]) if len(vix_hist) >= 2 else None
        vix_change = round(vix_val - vix_prev, 2) if vix_val and vix_prev else None
        vix_zone, vix_signal = _vix_zone(vix_val)
        result["vix"] = {
            "value": vix_val,
            "change_1d": vix_change,
            "zone": vix_zone,
            "signal": vix_signal,
            "interpretation": (
                "Extreme fear — market crisis" if vix_zone == "crisis"
                else "High fear — be very selective" if vix_zone == "high_fear"
                else "Elevated fear — cautious risk-taking" if vix_zone == "elevated_fear"
                else "Normal range — healthy market" if vix_zone == "calm"
                else "Very low — possible complacency, watch for reversal"
            ),
        }
    except Exception as e:
        result["vix"] = {"error": str(e)}

    # --- Yield Curve: 10Y minus 3M ---
    try:
        tnx = yf.Ticker("^TNX").history(period="5d")  # 10-year
        irx = yf.Ticker("^IRX").history(period="5d")  # 3-month
        rate_10y = _safe_float(tnx["Close"].iloc[-1] / 10) if not tnx.empty else None  # yfinance gives 10x
        rate_3m = _safe_float(irx["Close"].iloc[-1] / 10) if not irx.empty else None
        spread = round(rate_10y - rate_3m, 3) if rate_10y and rate_3m else None
        curve_shape, curve_signal = _yield_curve_zone(spread)
        result["yield_curve"] = {
            "rate_10y_pct": rate_10y,
            "rate_3m_pct": rate_3m,
            "spread_pct": spread,
            "shape": curve_shape,
            "signal": curve_signal,
            "interpretation": (
                "Inverted \u2014 historically precedes recession by 12-18 months" if curve_shape == "inverted"
                else "Flattening \u2014 watch for further compression" if curve_shape == "flattening"
                else "Normal/Steep \u2014 healthy credit conditions"
            ),
        }
    except Exception as e:
        result["yield_curve"] = {"error": str(e)}
        curve_shape = "unknown"

    # --- DXY (US Dollar Index) ---
    try:
        dxy_hist = yf.Ticker("DX-Y.NYB").history(period="30d")
        dxy_curr = _safe_float(dxy_hist["Close"].iloc[-1]) if not dxy_hist.empty else None
        dxy_30d_ago = _safe_float(dxy_hist["Close"].iloc[0]) if len(dxy_hist) >= 2 else None
        dxy_change_pct = (
            round((dxy_curr - dxy_30d_ago) / dxy_30d_ago * 100, 2)
            if dxy_curr and dxy_30d_ago
            else None
        )
        result["dxy"] = {
            "value": dxy_curr,
            "change_30d_pct": dxy_change_pct,
            "trend": _dxy_trend(dxy_change_pct),
        }
    except Exception as e:
        result["dxy"] = {"error": str(e)}

    # --- S&P 500 trend context ---
    try:
        spy_hist = yf.Ticker("^GSPC").history(period="1y")
        spy_price = _safe_float(spy_hist["Close"].iloc[-1]) if not spy_hist.empty else None
        spy_sma200 = _safe_float(spy_hist["Close"].rolling(200).mean().iloc[-1]) if len(spy_hist) >= 200 else None
        spy_trend = None
        if spy_price and spy_sma200:
            diff_pct = round((spy_price - spy_sma200) / spy_sma200 * 100, 2)
            spy_trend = f"above 200DMA by {diff_pct}%" if diff_pct > 0 else f"below 200DMA by {abs(diff_pct)}%"
        result["sp500"] = {
            "price": spy_price,
            "sma_200": spy_sma200,
            "trend": spy_trend,
            "signal": "🟢 bull market structure" if spy_price and spy_sma200 and spy_price > spy_sma200 else "🔴 bear market structure",
        }
    except Exception as e:
        result["sp500"] = {"error": str(e)}

    # --- Combined Macro Summary ---
    vix_zone_val = result.get("vix", {}).get("zone", "unknown")
    curve_shape_val = result.get("yield_curve", {}).get("shape", "unknown")
    result["macro_summary"] = _macro_summary(vix_zone_val, curve_shape_val)
    result["note"] = (
        "Run this before analysing any stock for macro context. "
        "VIX > 30 = avoid new positions unless contrarian. "
        "Inverted curve = prefer defensive/quality names."
    )

    return result
