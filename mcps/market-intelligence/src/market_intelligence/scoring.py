from market_intelligence.profile import get_full_profile_impl
from market_intelligence.technicals import get_technicals_impl
import yfinance as yf


def _safe(val, default=None):
    return val if val is not None else default


def _score_valuation(profile: dict) -> dict:
    """Max 25 points. Based on trailing PE + PEG ratio."""
    val = profile.get("valuation", {})
    pe = _safe(val.get("pe_trailing"))
    peg = _safe(val.get("peg_ratio"))

    if pe is None:
        return {"score": 10, "max": 25, "reason": "PE not available — neutral score applied"}

    if pe < 15:
        base = 23 if (peg and peg < 1) else 20
        reason = f"PE={pe:.1f} (very low)" + (f", PEG={peg:.2f} (< 1)" if peg and peg < 1 else "")
    elif pe < 20:
        base = 20 if (peg and peg < 1.5) else 17
        reason = f"PE={pe:.1f} (low)" + (f", PEG={peg:.2f}" if peg else "")
    elif pe < 25:
        base = 15
        reason = f"PE={pe:.1f} (fair)"
    elif pe < 35:
        base = 10
        reason = f"PE={pe:.1f} (elevated)"
    elif pe < 50:
        base = 5
        reason = f"PE={pe:.1f} (high)"
    else:
        base = 2
        reason = f"PE={pe:.1f} (very high)"

    # PEG bonus: +2 if PEG < 1 and base < 23
    if peg and peg < 1 and base < 23:
        base = min(base + 2, 25)
        reason += f" + PEG bonus (PEG={peg:.2f})"

    return {"score": min(base, 25), "max": 25, "reason": reason}


def _score_quality(profile: dict) -> dict:
    """Max 25 points: ROE sub (0-15) + insider% sub (0-5) + moat raw data (0-5)."""
    qual = profile.get("quality", {})
    risk = profile.get("risk", {})

    roe = _safe(qual.get("roe"))
    debt_to_equity = _safe(qual.get("debt_to_equity"))
    profit_margin = _safe(qual.get("profit_margin"))
    insider_pct = _safe(risk.get("insider_pct"))

    # ROE sub-score (0-15)
    if roe is None:
        roe_score = 6
        roe_reason = "ROE unavailable"
    elif roe > 0.15:
        roe_score = 15
        roe_reason = f"ROE={roe*100:.1f}% (excellent)"
    elif roe > 0.12:
        roe_score = 12
        roe_reason = f"ROE={roe*100:.1f}% (good)"
    elif roe > 0.08:
        roe_score = 9
        roe_reason = f"ROE={roe*100:.1f}% (acceptable)"
    else:
        roe_score = 5
        roe_reason = f"ROE={roe*100:.1f}% (weak)"

    # D/E penalty
    if debt_to_equity and debt_to_equity > 200:
        roe_score = max(roe_score - 3, 0)
        roe_reason += f", D/E penalty (D/E={debt_to_equity:.0f})"

    # Insider sub-score (0-5)
    if insider_pct is None:
        insider_score = 2
        insider_reason = "Insider% unavailable"
    elif insider_pct > 0.10:
        insider_score = 5
        insider_reason = f"Insider={insider_pct*100:.1f}% (strong skin-in-game)"
    elif insider_pct > 0.05:
        insider_score = 3
        insider_reason = f"Insider={insider_pct*100:.1f}% (moderate)"
    else:
        insider_score = 1
        insider_reason = f"Insider={insider_pct*100:.1f}% (low)"

    # Moat sub-score (0-5): raw data for Claude to assess
    moat_raw = {
        "profit_margin": profit_margin,
        "operating_margin": qual.get("operating_margin"),
        "gross_margin": qual.get("gross_margin"),
        "roe": roe,
        "note": "Claude should assess moat from margins + ROE consistency. Score suggestion: 5=wide moat, 3=narrow, 1=none.",
    }
    moat_score = 3  # neutral default, Claude can override using raw data

    total = min(roe_score + insider_score + moat_score, 25)
    return {
        "score": total,
        "max": 25,
        "reason": f"{roe_reason}; {insider_reason}; moat=raw (Claude assessment needed)",
        "moat_raw": moat_raw,
    }


def _compute_piotroski(symbol: str) -> dict:
    """Compute Piotroski F-Score (0-9): 9-point financial health check used by quant funds.
    Score 8-9 = Strong | 5-7 = Average | 0-4 = Weak.
    All 9 criteria use annual financial statement data from yfinance.
    """
    result = {"score": None, "criteria": {}, "error": None}
    try:
        ticker = yf.Ticker(symbol)
        cf = ticker.cashflow
        bs = ticker.balance_sheet
        inc = ticker.income_stmt
        info = ticker.info or {}
    except Exception as e:
        result["error"] = f"Could not fetch statements: {e}"
        return result

    def _row(df, *keys):
        """Get most recent and prior year values for a statement row."""
        if df is None or df.empty:
            return None, None
        for k in keys:
            if k in df.index:
                vals = []
                for i in range(min(2, df.shape[1])):
                    try:
                        vals.append(float(df.loc[k].iloc[i]))
                    except Exception:
                        vals.append(None)
                curr = vals[0] if vals else None
                prev = vals[1] if len(vals) > 1 else None
                return curr, prev
        return None, None

    # Extract statement data
    net_income_curr, net_income_prev = _row(inc, "Net Income", "Net Income Common Stockholders")
    cfo_curr, _ = _row(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
    total_assets_curr, total_assets_prev = _row(bs, "Total Assets")
    long_debt_curr, long_debt_prev = _row(bs, "Long Term Debt", "Long-Term Debt")
    curr_assets_curr, curr_assets_prev = _row(bs, "Current Assets")
    curr_liab_curr, curr_liab_prev = _row(bs, "Current Liabilities")
    gross_profit_curr, gross_profit_prev = _row(inc, "Gross Profit")
    revenue_curr, revenue_prev = _row(inc, "Total Revenue")
    shares_curr = info.get("sharesOutstanding")
    shares_prev = info.get("sharesOutstanding")  # YoY share change via info is approximate

    criteria = {}
    score = 0

    # === PROFITABILITY (4 pts) ===
    # F1: ROA positive
    roa = (net_income_curr / total_assets_curr) if net_income_curr and total_assets_curr else None
    f1 = 1 if roa and roa > 0 else 0
    criteria["F1_ROA_positive"] = {"value": round(roa, 4) if roa else None, "pass": bool(f1)}
    score += f1

    # F2: Operating Cash Flow positive
    f2 = 1 if cfo_curr and cfo_curr > 0 else 0
    criteria["F2_CFO_positive"] = {"value": cfo_curr, "pass": bool(f2)}
    score += f2

    # F3: ROA increasing YoY
    roa_prev = (net_income_prev / total_assets_prev) if net_income_prev and total_assets_prev else None
    f3 = 1 if (roa and roa_prev and roa > roa_prev) else 0
    criteria["F3_ROA_improving"] = {"value": round(roa - roa_prev, 4) if roa and roa_prev else None, "pass": bool(f3)}
    score += f3

    # F4: Accrual quality (CFO/Assets > ROA)
    cfo_to_assets = (cfo_curr / total_assets_curr) if cfo_curr and total_assets_curr else None
    f4 = 1 if (cfo_to_assets and roa and cfo_to_assets > roa) else 0
    criteria["F4_accrual_quality"] = {"value": round(cfo_to_assets, 4) if cfo_to_assets else None, "pass": bool(f4)}
    score += f4

    # === LEVERAGE / LIQUIDITY (3 pts) ===
    # F5: Long-term leverage decreased
    lev_curr = (long_debt_curr / total_assets_curr) if long_debt_curr and total_assets_curr else None
    lev_prev = (long_debt_prev / total_assets_prev) if long_debt_prev and total_assets_prev else None
    f5 = 1 if (lev_curr is not None and lev_prev is not None and lev_curr < lev_prev) else 0
    criteria["F5_leverage_decreased"] = {"value": round(lev_curr, 4) if lev_curr else None, "pass": bool(f5)}
    score += f5

    # F6: Current ratio improved
    cr_curr = (curr_assets_curr / curr_liab_curr) if curr_assets_curr and curr_liab_curr else None
    cr_prev = (curr_assets_prev / curr_liab_prev) if curr_assets_prev and curr_liab_prev else None
    f6 = 1 if (cr_curr is not None and cr_prev is not None and cr_curr > cr_prev) else 0
    criteria["F6_current_ratio_improved"] = {"value": round(cr_curr, 4) if cr_curr else None, "pass": bool(f6)}
    score += f6

    # F7: No new shares issued (no dilution)
    shares_issued_curr, shares_issued_prev = _row(cf, "Issuance Of Stock", "Stock Issuance", "Common Stock Issuance")
    f7 = 1 if (shares_issued_curr is None or shares_issued_curr <= 0) else 0
    criteria["F7_no_new_shares"] = {"value": shares_issued_curr, "pass": bool(f7)}
    score += f7

    # === EFFICIENCY (2 pts) ===
    # F8: Gross margin improved
    gm_curr = (gross_profit_curr / revenue_curr) if gross_profit_curr and revenue_curr else None
    gm_prev = (gross_profit_prev / revenue_prev) if gross_profit_prev and revenue_prev else None
    f8 = 1 if (gm_curr is not None and gm_prev is not None and gm_curr > gm_prev) else 0
    criteria["F8_gross_margin_improved"] = {"value": round(gm_curr, 4) if gm_curr else None, "pass": bool(f8)}
    score += f8

    # F9: Asset turnover improved
    at_curr = (revenue_curr / total_assets_curr) if revenue_curr and total_assets_curr else None
    at_prev = (revenue_prev / total_assets_prev) if revenue_prev and total_assets_prev else None
    f9 = 1 if (at_curr is not None and at_prev is not None and at_curr > at_prev) else 0
    criteria["F9_asset_turnover_improved"] = {"value": round(at_curr, 4) if at_curr else None, "pass": bool(f9)}
    score += f9

    # Verdict
    if score >= 8:
        verdict = "strong"
    elif score >= 5:
        verdict = "average"
    else:
        verdict = "weak"

    result["score"] = score
    result["max"] = 9
    result["verdict"] = verdict
    result["criteria"] = criteria
    result["note"] = (
        f"Piotroski F-Score {score}/9 ({verdict.upper()}). "
        "8-9=Strong (quant buy signal) | 5-7=Average | 0-4=Weak (potential value trap)"
    )
    return result


def _compute_squeeze(profile: dict, technicals: dict) -> dict:
    """Short Squeeze Detector. Criteria: high short %, high days-to-cover, rising volume, positive momentum."""
    risk = profile.get("risk", {})
    short_pct = risk.get("short_pct_of_float")  # as decimal (0.15 = 15%)
    short_ratio = risk.get("short_ratio")        # days to cover
    price_data = profile.get("price", {})
    volume = price_data.get("volume")
    avg_volume = price_data.get("avg_volume")
    rel_volume = round(volume / avg_volume, 2) if volume and avg_volume else None

    tech_signals = technicals.get("signals", {})
    tech_momentum = technicals.get("momentum", {})
    rsi = tech_momentum.get("rsi_14")

    score = 0
    flags = []

    if short_pct and short_pct > 0.10:
        score += 1
        flags.append(f"Short% {short_pct*100:.1f}% > 10%")
    if short_pct and short_pct > 0.20:
        score += 1  # double credit for extreme short interest
        flags.append(f"Short% {short_pct*100:.1f}% > 20% (extremely crowded)")
    if short_ratio and short_ratio > 5:
        score += 1
        flags.append(f"Days-to-cover {short_ratio:.1f} > 5 (exit difficult)")
    if rel_volume and rel_volume > 1.5:
        score += 1
        flags.append(f"Relative volume {rel_volume}x > 1.5x (active buying)")
    if rsi and 50 <= rsi <= 70:
        score += 1
        flags.append(f"RSI {rsi:.1f} in 50-70 zone (momentum up, not overbought)")

    if score >= 4:
        verdict = "high"
        note = "HIGH squeeze potential — dangerous for short sellers, treat as risk factor for longs too"
    elif score >= 2:
        verdict = "moderate"
        note = "MODERATE squeeze risk — watch for volume spikes"
    else:
        verdict = "low"
        note = "LOW squeeze risk — no unusual short pressure"

    return {
        "score": score,
        "max": 5,
        "verdict": verdict,
        "short_pct_of_float": f"{short_pct*100:.1f}%" if short_pct else None,
        "days_to_cover": short_ratio,
        "relative_volume": rel_volume,
        "flags": flags,
        "note": note,
    }


def _score_momentum(technicals: dict) -> dict:
    """Max 25 points: 5 signals × 5 pts each + 52W High bonus (up to +3 pts, capped at 25)."""
    if "error" in technicals:
        return {"score": 10, "max": 25, "reason": f"Technicals unavailable: {technicals['error']}"}

    trend = technicals.get("trend", {})
    momentum = technicals.get("momentum", {})
    strength = technicals.get("strength", {})
    mf = technicals.get("momentum_factor", {})

    above_200 = trend.get("above_200dma", False)
    above_50 = trend.get("above_50dma", False)
    rsi = momentum.get("rsi_14")
    macd_bullish = momentum.get("macd_bullish", False)
    adx = strength.get("adx_14")
    w52_signal = mf.get("signal") if mf and "error" not in mf else None

    score = 0
    reasons = []

    if above_200:
        score += 5
        reasons.append("above 200DMA")
    if above_50:
        score += 5
        reasons.append("above 50DMA")
    if rsi and 45 <= rsi <= 65:
        score += 5
        reasons.append(f"RSI={rsi:.1f} (ideal zone)")
    elif rsi:
        reasons.append(f"RSI={rsi:.1f} (outside 45-65)")
    if macd_bullish:
        score += 5
        reasons.append("MACD bullish")
    if adx and adx > 25:
        score += 5
        reasons.append(f"ADX={adx:.1f} (strong trend)")
    elif adx:
        reasons.append(f"ADX={adx:.1f} (weak trend)")

    # 52-Week High Momentum Bonus (George & Hwang factor)
    if w52_signal == "at_or_above_52w_high":
        bonus = 3
        reasons.append("52W high bonus: at/above 52W high (+3)")
        score = min(score + bonus, 25)
    elif w52_signal == "near_52w_high":
        bonus = 2
        reasons.append("52W high bonus: within 5% of 52W high (+2)")
        score = min(score + bonus, 25)
    elif w52_signal == "far_from_high":
        reasons.append("52W penalty: >30% below 52W high")

    return {"score": score, "max": 25, "reason": "; ".join(reasons) if reasons else "No momentum signals"}


def _score_risk(profile: dict) -> dict:
    """Max 25 points based on Beta."""
    risk = profile.get("risk", {})
    beta = _safe(risk.get("beta"))

    if beta is None:
        return {"score": 15, "max": 25, "reason": "Beta unavailable — neutral score"}

    if 0.8 <= beta <= 1.2:
        score = 25
        reason = f"Beta={beta:.2f} (market-correlated, low volatility)"
    elif beta < 1.5:
        score = 20
        reason = f"Beta={beta:.2f} (slightly elevated)"
    elif beta < 2.0:
        score = 15
        reason = f"Beta={beta:.2f} (elevated volatility)"
    elif beta < 2.5:
        score = 10
        reason = f"Beta={beta:.2f} (high volatility)"
    else:
        score = 5
        reason = f"Beta={beta:.2f} (very high volatility)"

    return {"score": score, "max": 25, "reason": reason}


def _verdict(total: int) -> str:
    if total >= 80:
        return "BUY"
    if total >= 65:
        return "BUY/HOLD"
    if total >= 50:
        return "HOLD"
    if total >= 35:
        return "HOLD/SELL"
    return "SELL"


def get_scoring_data_impl(symbol: str) -> dict:
    profile = get_full_profile_impl(symbol)
    if "error" in profile:
        return {"symbol": symbol, "error": profile["error"]}

    technicals = get_technicals_impl(symbol)

    # Deal-breaker checks
    deal_breakers = []
    qual = profile.get("quality", {})
    current_ratio = qual.get("current_ratio")
    debt_to_equity = qual.get("debt_to_equity")
    growth = profile.get("growth", {})
    revenue = growth.get("revenue")
    net_income = growth.get("net_income")

    if current_ratio is not None and current_ratio < 0.5:
        deal_breakers.append(f"Solvency risk: current_ratio={current_ratio:.2f} (< 0.5)")
    if debt_to_equity is not None and debt_to_equity > 500:
        deal_breakers.append(f"Overleveraged: debt_to_equity={debt_to_equity:.0f} (> 500)")
    if (revenue is None or revenue == 0) and (net_income is None or net_income == 0):
        deal_breakers.append("Uninvestable: no revenue and no earnings data")

    if deal_breakers:
        return {
            "symbol": symbol,
            "blocked": True,
            "deal_breakers": deal_breakers,
            "raw_profile": profile,
            "raw_technicals": technicals,
        }

    v = _score_valuation(profile)
    q = _score_quality(profile)
    m = _score_momentum(technicals)
    r = _score_risk(profile)

    total = v["score"] + q["score"] + m["score"] + r["score"]

    # Piotroski F-Score
    piotroski = _compute_piotroski(symbol)

    # Short Squeeze Detector
    squeeze = _compute_squeeze(profile, technicals)

    # Earnings Quality modifier (bonus/penalty applied to quality score)
    eq = profile.get("earnings_quality", {})
    eq_rating = eq.get("earnings_quality", "unavailable")
    eq_note = ""
    if eq_rating == "excellent":
        total = min(total + 3, 100)
        eq_note = "+3 earnings quality bonus (FCF > NI)"
    elif eq_rating == "good":
        total = min(total + 1, 100)
        eq_note = "+1 earnings quality bonus"
    elif eq_rating == "warning":
        total = max(total - 2, 0)
        eq_note = "-2 earnings quality penalty"
    elif eq_rating == "poor":
        total = max(total - 4, 0)
        eq_note = "-4 earnings quality penalty"
    elif eq_rating == "red_flag":
        total = max(total - 8, 0)
        eq_note = "-8 earnings quality: red flag (negative FCF with positive NI)"

    # Piotroski modifier on total
    f_score = piotroski.get("score")
    piotroski_note = ""
    if f_score is not None:
        if f_score >= 8:
            total = min(total + 5, 100)
            piotroski_note = f"+5 Piotroski F={f_score}/9 (strong)"
        elif f_score >= 5:
            piotroski_note = f"Piotroski F={f_score}/9 (average, no modifier)"
        else:
            total = max(total - 5, 0)
            piotroski_note = f"-5 Piotroski F={f_score}/9 (weak — potential value trap)"

    return {
        "symbol": symbol,
        "blocked": False,
        "deal_breakers": [],
        "pillar_scores": {
            "valuation": v,
            "quality": q,
            "momentum": m,
            "risk": r,
        },
        "modifiers": {
            "earnings_quality": eq_note,
            "piotroski": piotroski_note,
        },
        "total_score": total,
        "verdict_suggestion": _verdict(total),
        "piotroski_f_score": piotroski,
        "short_squeeze": squeeze,
        "raw_profile": profile,
        "raw_technicals": technicals,
    }
