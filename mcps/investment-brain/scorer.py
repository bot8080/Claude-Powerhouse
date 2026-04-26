"""Scoring Engine - Implements the full 35/35/30 rubric.

Maps raw MCP/yfinance data to Fundamentals (35), Technicals (35), Smart Money (30).
Applies sector overrides and moat adjustments.
"""

from typing import Dict, Optional, Any
from config import (
    FUNDAMENTALS_MAX, TECHNICALS_MAX, SMART_MONEY_MAX,
    SECTOR_OVERRIDES, PE_SCALE, PEG_SCALE, EV_EBITDA_SCALE,
    ROE_SCALE, OP_MARGIN_SCALE, DE_SCALE, CURR_RATIO_SCALE,
    RSI_SCALE
)


def score_stock(data: Dict, sector: str = "", moat: str = "none") -> Dict:
    """Score a stock using the 35/35/30 framework.

    Args:
        data: Stock data from DataFetcher
        sector: Sector name for overrides
        moat: "wide", "narrow", or "none"

    Returns:
        {
            "fundamentals": {"score": int, "max": 35, "breakdown": {...}},
            "technicals": {"score": int, "max": 35, "breakdown": {...}},
            "smart_money": {"score": int, "max": 30, "breakdown": {...}},
            "total": int,
            "verdict": str,
            "account": str,
            "stop_loss": float,
            "price_zones": {...},
        }
    """
    profile = _extract_profile(data)
    technicals = _extract_technicals(data)
    institutional = data.get("institutional", {})
    risk = profile.get("risk", {})
    analyst = profile.get("analyst", {})

    # ─── Fundamentals (35) ───
    fund = _score_fundamentals(profile, sector)

    # ─── Technicals (35) ───
    tech = _score_technicals(technicals)

    # ─── Smart Money (30) ───
    sm = _score_smart_money(institutional, risk, analyst, data.get("market", "US"))

    # ─── Moat Override ───
    if moat == "wide":
        fund["score"] = min(fund["score"] + 2, FUNDAMENTALS_MAX)
    elif moat == "none":
        fund["score"] = max(fund["score"] - 2, 0)

    # ─── Total ───
    total = fund["score"] + tech["score"] + sm["score"]

    # ─── Verdict ───
    verdict = _derive_verdict(fund["score"], tech["score"], total)

    # ─── Price & Zones ───
    price = _get_price(profile)
    zones = _calc_price_zones(price, fund["score"], tech["score"])
    stop_loss = _calc_stop_loss(price, technicals)

    return {
        "fundamentals": fund,
        "technicals": tech,
        "smart_money": sm,
        "total": total,
        "verdict": verdict,
        "account": _suggest_account(data.get("market", "US"), profile),
        "stop_loss": stop_loss,
        "price_zones": zones,
        "moat": moat,
    }


def _extract_profile(data: Dict) -> Dict:
    """Extract profile from MCP or yfinance data."""
    if "mcp_scoring" in data and data["mcp_scoring"]:
        return data["mcp_scoring"].get("raw_profile", {})
    return data.get("profile", {})


def _extract_technicals(data: Dict) -> Dict:
    """Extract technicals from MCP or yfinance data."""
    if "mcp_scoring" in data and data["mcp_scoring"]:
        return data["mcp_scoring"].get("raw_technicals", {})
    return data.get("technicals", {})


def _score_fundamentals(profile: Dict, sector: str) -> Dict:
    """Score fundamentals out of 35."""
    val = profile.get("valuation", {})
    qual = profile.get("quality", {})
    growth = profile.get("growth", {})
    div = profile.get("dividends", {})

    # Override for sector
    override = SECTOR_OVERRIDES.get(sector, {})

    # ── Valuation (0-12) ──
    pe = _f(val.get("pe_trailing")) or _f(val.get("pe"))
    peg = _f(val.get("peg_ratio"))
    ev_ebitda = _f(val.get("ev_ebitda"))

    pe_score = _score_metric(pe, PE_SCALE, invert=False)
    peg_score = _score_metric(peg, PEG_SCALE, invert=False) if peg else pe_score
    ev_score = _score_metric(ev_ebitda, EV_EBITDA_SCALE, invert=False) if ev_ebitda else pe_score

    if override.get("skip_pe"):
        val_score = ev_score
    elif override.get("pe_weight", 1.0) < 1.0:
        val_score = int((pe_score * override["pe_weight"] + ev_score * (1.5 - override["pe_weight"])) / 1.5)
    else:
        val_score = int((pe_score + peg_score + ev_score) / 3)
    val_score = min(max(val_score, 0), 12)

    # ── Quality (0-13) ──
    roe = _f(qual.get("roe"))
    op_margin = _f(qual.get("operating_margin"))
    de = _f(qual.get("debt_to_equity"))
    curr_ratio = _f(qual.get("current_ratio"))
    fcf = _f(qual.get("free_cashflow"))

    roe_score = _score_metric(roe * 100 if roe and roe < 1 else roe, ROE_SCALE, invert=False)
    margin_score = _score_metric(op_margin * 100 if op_margin and op_margin < 1 else op_margin, OP_MARGIN_SCALE, invert=False)
    de_score = _score_metric(de, DE_SCALE, invert=True)
    curr_score = _score_metric(curr_ratio, CURR_RATIO_SCALE, invert=False)
    fcf_score = 4 if fcf and fcf > 0 else 2 if fcf and fcf == 0 else 0

    qual_score = int((roe_score + margin_score + de_score + curr_score + fcf_score) / 5 * 13 / 4)
    qual_score = min(max(qual_score, 0), 13)

    # ── Growth (0-5) ──
    rev_g = _f(growth.get("revenue_growth"))
    earn_g = _f(growth.get("earnings_growth"))
    if rev_g is not None and earn_g is not None:
        if rev_g > 15 and earn_g > rev_g:
            growth_score = 5
        elif rev_g > 10:
            growth_score = 4
        elif rev_g > 5:
            growth_score = 3
        elif rev_g > 0:
            growth_score = 2
        else:
            growth_score = 0
    elif rev_g is not None:
        growth_score = 4 if rev_g > 15 else 3 if rev_g > 10 else 2 if rev_g > 5 else 1 if rev_g > 0 else 0
    else:
        growth_score = 2  # neutral if unknown

    # ── Dividends (0-5) ──
    yield_pct = _f(div.get("yield"))
    payout = _f(div.get("payout_ratio"))
    if override.get("dividend_weight", 1.0) > 1.0:
        # REITs: dividends are the thesis
        div_score = 5 if yield_pct and 2 <= yield_pct <= 6 and payout and payout < 80 else 3 if yield_pct and yield_pct > 0 else 0
    else:
        if yield_pct and 2 <= yield_pct <= 6 and payout and payout < 60:
            div_score = 5
        elif yield_pct and 0 < yield_pct < 2:
            div_score = 3
        elif payout and payout > 80:
            div_score = 1
        else:
            div_score = 3 if not yield_pct else 0

    total = val_score + qual_score + growth_score + div_score
    return {
        "score": min(total, FUNDAMENTALS_MAX),
        "max": FUNDAMENTALS_MAX,
        "breakdown": {
            "valuation": val_score,
            "quality": qual_score,
            "growth": growth_score,
            "dividends": div_score,
        },
        "raw": {
            "pe": pe, "peg": peg, "ev_ebitda": ev_ebitda,
            "roe": roe, "op_margin": op_margin, "de": de,
            "curr_ratio": curr_ratio, "fcf": fcf,
            "rev_growth": rev_g, "earn_growth": earn_g,
            "div_yield": yield_pct, "payout": payout,
        }
    }


def _score_technicals(tech: Dict) -> Dict:
    """Score technicals out of 35."""
    trend = tech.get("trend", {})
    momentum = tech.get("momentum", {})
    volatility = tech.get("volatility", {})
    strength = tech.get("strength", {})
    volume = tech.get("volume", {})
    signals = tech.get("signals", {})

    # ── Trend (0-10) ──
    above_200 = trend.get("above_200dma", False)
    above_50 = trend.get("above_50dma", False)
    golden = trend.get("golden_cross", False)
    death = trend.get("death_cross", False)

    if golden:
        trend_score = 10
    elif above_200 and above_50:
        trend_score = 8
    elif above_200:
        trend_score = 5
    elif not above_50:
        trend_score = 2
    else:
        trend_score = 5
    if death:
        trend_score = 0

    # ── Momentum (0-10) ──
    rsi = _f(momentum.get("rsi_14"))
    macd_bull = momentum.get("macd_bullish", False)

    if rsi is not None:
        if 45 <= rsi <= 65 and macd_bull:
            mom_score = 10
        elif 45 <= rsi <= 65 or macd_bull:
            mom_score = 7
        elif 30 <= rsi < 45 or 65 < rsi <= 70:
            mom_score = 5
        elif rsi < 30 or rsi > 70:
            mom_score = 2
        else:
            mom_score = 5
    else:
        mom_score = 5 if macd_bull else 3

    # ── Volatility (0-5) ──
    atr_pct = _f(volatility.get("atr_pct"))
    bb_pct = _f(volatility.get("bb_pct_b"))
    if atr_pct is not None and bb_pct is not None:
        if 1 <= atr_pct <= 3 and 0.2 <= bb_pct <= 0.8:
            vol_score = 5
        elif atr_pct > 5 or bb_pct > 1:
            vol_score = 1
        elif bb_pct < 0:
            vol_score = 0
        else:
            vol_score = 3
    else:
        vol_score = 3

    # ── Strength + Volume (0-10) ──
    adx = _f(strength.get("adx_14"))
    obv = volume.get("obv_trend", "flat")
    mfi = _f(volume.get("mfi_14"))
    vol_ratio = _f(volume.get("volume_vs_avg_20d"))
    direction = strength.get("trend_direction", "neutral")

    if adx is not None and adx > 25 and direction == "bullish" and obv == "rising":
        sv_score = 10
    elif adx and adx > 20 and direction == "bullish":
        sv_score = 7
    elif adx and adx < 20:
        sv_score = 4
    elif direction == "bearish" and obv == "falling":
        sv_score = 0
    else:
        sv_score = 5

    total = trend_score + mom_score + vol_score + sv_score
    return {
        "score": min(total, TECHNICALS_MAX),
        "max": TECHNICALS_MAX,
        "breakdown": {
            "trend": trend_score,
            "momentum": mom_score,
            "volatility": vol_score,
            "strength_volume": sv_score,
        },
        "raw": {
            "rsi": rsi, "macd_bullish": macd_bull,
            "above_200dma": above_200, "above_50dma": above_50,
            "golden_cross": golden, "death_cross": death,
            "adx": adx, "obv": obv, "mfi": mfi,
            "atr_pct": atr_pct, "bb_pct_b": bb_pct,
        }
    }


def _score_smart_money(inst: Dict, risk: Dict, analyst: Dict, market: str) -> Dict:
    """Score smart money out of 30."""
    # For Indian stocks, data is limited
    if market == "IN":
        return {
            "score": 15,  # neutral baseline
            "max": SMART_MONEY_MAX,
            "breakdown": {
                "insider": 3, "institutional": 3, "short": 3,
                "analyst": 3, "governance": 3,
            },
            "raw": {},
            "note": "Indian stock: limited institutional data"
        }

    insider_pct = _f(risk.get("insider_pct"))
    inst_pct = _f(risk.get("institution_pct"))
    short_pct = _f(risk.get("short_pct_float"))
    short_ratio = _f(risk.get("short_ratio"))
    target = _f(analyst.get("target_mean"))
    rating = analyst.get("recommendation", "")
    overall_risk = _f(risk.get("overall_risk"))
    beta = _f(risk.get("beta"))

    # Insider (0-8)
    if insider_pct is not None:
        if insider_pct > 10:
            ins_score = 8
        elif insider_pct > 5:
            ins_score = 6
        elif insider_pct > 3:
            ins_score = 4
        else:
            ins_score = 2
    else:
        ins_score = 4

    # Institutional (0-7)
    if inst_pct is not None:
        if 60 <= inst_pct <= 85:
            inst_score = 7
        elif 40 <= inst_pct < 60:
            inst_score = 5
        elif inst_pct < 40:
            inst_score = 3
        else:
            inst_score = 3  # >85% crowded
    else:
        inst_score = 4

    # Short interest (0-5)
    if short_pct is not None:
        if short_pct < 3:
            short_score = 5
        elif short_pct < 10:
            short_score = 3
        else:
            short_score = 1
    elif short_ratio is not None:
        if short_ratio < 3:
            short_score = 5
        elif short_ratio < 7:
            short_score = 3
        else:
            short_score = 1
    else:
        short_score = 3

    # Analyst (0-5)
    if target and analyst.get("target_mean"):
        # Can't compute upside without price - handled in prompt builder
        if "buy" in rating.lower():
            ana_score = 5
        elif "hold" in rating.lower():
            ana_score = 3
        elif "sell" in rating.lower():
            ana_score = 1
        else:
            ana_score = 3
    else:
        ana_score = 3

    # Governance (0-5)
    if overall_risk is not None:
        if 1 <= overall_risk <= 3:
            gov_score = 5
        elif overall_risk <= 6:
            gov_score = 3
        else:
            gov_score = 1
    else:
        gov_score = 3

    total = ins_score + inst_score + short_score + ana_score + gov_score
    return {
        "score": min(total, SMART_MONEY_MAX),
        "max": SMART_MONEY_MAX,
        "breakdown": {
            "insider": ins_score,
            "institutional": inst_score,
            "short_interest": short_score,
            "analyst": ana_score,
            "governance": gov_score,
        },
        "raw": {
            "insider_pct": insider_pct,
            "institution_pct": inst_pct,
            "short_pct": short_pct,
            "short_ratio": short_ratio,
            "target": target,
            "rating": rating,
            "overall_risk": overall_risk,
            "beta": beta,
        }
    }


def _derive_verdict(fund: int, tech: int, total: int) -> str:
    """Derive verdict from scores."""
    if total >= 80:
        return "BUY"
    elif total >= 65:
        return "BUY-HOLD"
    elif total >= 50:
        return "HOLD"
    elif total >= 35:
        return "WAIT"
    else:
        return "SELL"


def _calc_price_zones(price: float, fund: int, tech: int) -> Dict:
    """Calculate price zones based on valuation and technicals."""
    if price <= 0:
        return {}

    # Simple zone calculation based on fundamentals
    if fund >= 25:
        discount = 0.15
    elif fund >= 17:
        discount = 0.10
    else:
        discount = 0.05

    excellent = price * (1 - discount)
    good = price * (1 - discount * 0.5)
    fair = price * 1.05
    expensive = price * 1.15

    return {
        "excellent": round(excellent, 2),
        "good": round(good, 2),
        "fair": round(fair, 2),
        "expensive": round(expensive, 2),
        "current": price,
    }


def _calc_stop_loss(price: float, tech: Dict) -> float:
    """Calculate ATR-based stop loss."""
    if price <= 0:
        return 0
    atr_pct = _f(tech.get("volatility", {}).get("atr_pct"))
    if atr_pct and atr_pct > 0:
        return round(price * (1 - min(atr_pct * 2, 15) / 100), 2)
    return round(price * 0.9, 2)


def _suggest_account(market: str, profile: Dict) -> str:
    """Suggest best account type."""
    from config import ACCOUNT_MAP
    base = ACCOUNT_MAP.get(market, "TFSA")

    # US dividend stocks better in RRSP
    if market == "US":
        div_yield = _f(profile.get("dividends", {}).get("yield"))
        if div_yield and div_yield > 1.5:
            return "RRSP"
    return base


def _f(val) -> Optional[float]:
    """Safely convert to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _score_metric(value: Optional[float], scale: Dict, invert: bool = False) -> int:
    """Score a metric against a scale.

    scale = {"green": threshold, "yellow": threshold, "red": threshold}
    Returns 0-4 scale (mapped to sub-score ranges).
    """
    if value is None:
        return 2  # neutral if unknown

    green = scale.get("green", 0)
    yellow = scale.get("yellow", 0)
    red = scale.get("red", 999)

    if invert:
        # Lower is better (e.g., D/E)
        if value <= green:
            return 4
        elif value <= yellow:
            return 3
        elif value <= red:
            return 1
        else:
            return 0
    else:
        # Higher is better (e.g., ROE)
        if value >= green:
            return 4
        elif value >= yellow:
            return 3
        elif value >= 0:
            return 1
        else:
            return 0
