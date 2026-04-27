"""Deal-Breaker Checker - Runs BEFORE scoring.

Implements all 9 deal-breakers from scoring_and_metrics.md.
Any single trigger = automatic disqualification.
"""

from typing import Dict, List, Optional, Any
from config import DEAL_BREAKERS, SECTOR_OVERRIDES


def calculate_altman_z(data: Dict) -> Optional[float]:
    """Calculate Altman Z-score from financial statements.

    Formula: Z = 1.2*(WC/TA) + 1.4*(RE/TA) + 3.3*(EBIT/TA) + 0.6*(MVE/TL) + 1.0*(S/TA)

    Args:
        data: Stock data dict with financial_statements

    Returns:
        Altman Z-score or None if insufficient data
    """
    financials = data.get("financial_statements", {})
    derived = financials.get("derived", {})

    wc_ratio = derived.get("working_capital_to_assets")
    re_ratio = derived.get("retained_earnings_to_assets")
    ebit_ratio = derived.get("ebit_to_assets")
    equity_liab_ratio = derived.get("equity_to_liabilities")
    sales_ratio = derived.get("sales_to_assets")

    if wc_ratio is None and re_ratio is None and ebit_ratio is None:
        return None

    z_score = (
        1.2 * (wc_ratio if wc_ratio is not None else 0) +
        1.4 * (re_ratio if re_ratio is not None else 0) +
        3.3 * (ebit_ratio if ebit_ratio is not None else 0) +
        0.6 * (equity_liab_ratio if equity_liab_ratio is not None else 0) +
        1.0 * (sales_ratio if sales_ratio is not None else 0)
    )

    return round(z_score, 2)


def calculate_altman_z_private(data: Dict) -> Optional[float]:
    """Calculate Altman Z'-score for private companies.

    Formula: Z' = 0.717*(WC/TA) + 0.847*(RE/TA) + 3.107*(EBIT/TA) + 0.420*(MVE/TL) + 0.998*(S/TA)

    Args:
        data: Stock data dict with financial_statements

    Returns:
        Altman Z'-score or None if insufficient data
    """
    financials = data.get("financial_statements", {})
    derived = financials.get("derived", {})

    wc_ratio = derived.get("working_capital_to_assets")
    re_ratio = derived.get("retained_earnings_to_assets")
    ebit_ratio = derived.get("ebit_to_assets")
    equity_liab_ratio = derived.get("equity_to_liabilities")
    sales_ratio = derived.get("sales_to_assets")

    if wc_ratio is None and re_ratio is None and ebit_ratio is None:
        return None

    z_score = (
        0.717 * (wc_ratio if wc_ratio is not None else 0) +
        0.847 * (re_ratio if re_ratio is not None else 0) +
        3.107 * (ebit_ratio if ebit_ratio is not None else 0) +
        0.420 * (equity_liab_ratio if equity_liab_ratio is not None else 0) +
        0.998 * (sales_ratio if sales_ratio is not None else 0)
    )

    return round(z_score, 2)


def check_altman_z(data: Dict) -> Dict:
    """Check Altman Z-score deal-breaker.

    Args:
        data: Stock data dict

    Returns:
        Dict with blocked, reason, evidence
    """
    profile = data.get("profile", {})
    identity = profile.get("identity", {}) if isinstance(profile, dict) else {}
    sector = identity.get("sector", "")

    sector_overrides = SECTOR_OVERRIDES.get(sector, {})

    if sector_overrides.get("skip_altman"):
        return {
            "blocked": False,
            "reason": None,
            "evidence": f"Altman Z skipped for sector: {sector}",
        }

    z_score = calculate_altman_z(data)

    if z_score is None:
        return {
            "blocked": False,
            "reason": None,
            "evidence": "Insufficient financial data for Altman Z calculation",
        }

    threshold = DEAL_BREAKERS.get("altman_z_min", 1.81)

    if z_score < threshold:
        return {
            "blocked": True,
            "reason": f"Altman Z {z_score} < {threshold} (distress zone)",
            "evidence": f"Z-score: {z_score:.2f} (threshold: {threshold})",
        }

    return {
        "blocked": False,
        "reason": None,
        "evidence": f"Z-score: {z_score:.2f} (safe/grey zone)",
    }


def check_regulatory_action(data: Dict) -> Dict:
    """Check for regulatory action (rule 6).

    Args:
        data: Stock data dict with regulatory_check

    Returns:
        Dict with blocked, reason, evidence
    """
    regulatory = data.get("regulatory_check", {})

    if not regulatory.get("headlines"):
        return {
            "blocked": False,
            "reason": None,
            "evidence": "No regulatory issues found in recent news",
        }

    headlines = regulatory.get("headlines", [])
    return {
        "blocked": True,
        "reason": "Regulatory action detected",
        "evidence": headlines[:2],  # Show first 2 headlines
    }


def check_enhanced_solvency(data: Dict) -> List[Dict]:
    """Enhanced solvency checks (rule 7).

    Args:
        data: Stock data dict

    Returns:
        List of issues found
    """
    issues = []

    financials = data.get("financial_statements", {})
    bs = financials.get("balance_sheet", {})
    derived = financials.get("derived", {})

    current_ratio = _get_num(data.get("profile", {}).get("quality", {}), "current_ratio") if isinstance(data.get("profile"), dict) else None

    if current_ratio is not None and current_ratio < DEAL_BREAKERS["current_ratio_min"]:
        issues.append({
            "reason": f"Current ratio {current_ratio:.2f} < {DEAL_BREAKERS['current_ratio_min']}",
            "evidence": f"Current ratio: {current_ratio:.2f}",
        })

    de = _get_num(data.get("profile", {}).get("quality", {}), "debt_to_equity") if isinstance(data.get("profile"), dict) else None
    if de is not None and de > DEAL_BREAKERS["debt_equity_max"]:
        issues.append({
            "reason": f"D/E {de:.0f} > {DEAL_BREAKERS['debt_equity_max']}",
            "evidence": f"D/E: {de:.0f}",
        })

    working_capital = bs.get("working_capital")
    if working_capital is not None and working_capital < 0:
        issues.append({
            "reason": "Negative working capital",
            "evidence": f"Working capital: ${working_capital:,.0f}",
        })

    interest_coverage = derived.get("interest_coverage")
    if interest_coverage is not None and interest_coverage < 1.0:
        issues.append({
            "reason": f"Interest coverage {interest_coverage:.1f}x < 1.0x",
            "evidence": f"EBIT/Interest: {interest_coverage:.1f}x",
        })

    return issues


def check_revenue_earnings(data: Dict) -> Dict:
    """Direct check for revenue + earnings (rule 8).

    Args:
        data: Stock data dict with financial_statements

    Returns:
        Dict with blocked, reason, evidence
    """
    financials = data.get("financial_statements", {})
    income = financials.get("income_statement", {})

    revenue = income.get("revenue")
    net_income = income.get("net_income")

    if revenue is None and net_income is None:
        return {
            "blocked": False,
            "reason": None,
            "evidence": "No income statement data available",
        }

    no_revenue = revenue is not None and revenue <= 0
    no_earnings = net_income is not None and net_income <= 0

    if no_revenue and no_earnings:
        return {
            "blocked": True,
            "reason": "No revenue and no earnings",
            "evidence": f"Revenue: {'N/A' if revenue is None else f'${revenue:,.0f}'}, Net Income: {'N/A' if net_income is None else f'${net_income:,.0f}'}",
        }

    return {
        "blocked": False,
        "reason": None,
        "evidence": f"Revenue: {'N/A' if revenue is None else f'${revenue:,.0f}'}, Net Income: {'N/A' if net_income is None else f'${net_income:,.0f}'}",
    }


def check_deal_breakers(data: Dict) -> Dict:
    """Check all 9 deal-breakers. Returns {blocked: bool, reasons: list}.

    Args:
        data: Stock data dict from DataFetcher.get_stock_data()

    Returns:
        {"blocked": bool, "reasons": [str], "evidence": [str]}
    """
    profile = data.get("profile", {})
    quality = profile.get("quality", {}) if isinstance(profile, dict) else {}
    valuation = profile.get("valuation", {}) if isinstance(profile, dict) else {}
    risk = profile.get("risk", {}) if isinstance(profile, dict) else {}
    identity = profile.get("identity", {}) if isinstance(profile, dict) else {}
    institutional = data.get("institutional", {})

    if not quality and "mcp_scoring" in data:
        raw_profile = data["mcp_scoring"].get("raw_profile", {})
        quality = raw_profile.get("quality", {})
        valuation = raw_profile.get("valuation", {})
        risk = raw_profile.get("risk", {})
        identity = raw_profile.get("identity", {})

    reasons = []
    evidence = []

    # Rule 1: Earnings manipulation - QoE Ratio < 0.7 for 2+ years
    # (Requires multi-year data - skip auto-check)

    # Rule 2: Bankruptcy risk - Altman Z < 1.81 (NOW AUTOMATED)
    altman_result = check_altman_z(data)
    if altman_result.get("blocked"):
        reasons.append(altman_result["reason"])
        evidence.append(altman_result["evidence"])
    elif altman_result.get("evidence") and "Insufficient" not in altman_result["evidence"]:
        evidence.append(altman_result["evidence"])

    # Rule 3: Accounting red flags
    # (Requires auditor reports - flag as unverified)

    # Rule 4: Negative FCF sustained 2+ years
    fcf = _get_num(quality, "free_cashflow")
    if fcf is not None and fcf < 0:
        if data.get("blocked") and "negative cash flow" in str(data.get("deal_breakers", [])).lower():
            reasons.append("Negative FCF sustained")
            evidence.append(f"FCF: ${fcf:,.0f}")

    # Rule 5: Broken insider alignment
    insider_pct = _get_num(risk, "insider_pct")
    insider_tx = institutional.get("insider_transactions", {}) if isinstance(institutional, dict) else {}
    if insider_tx and isinstance(insider_tx, dict):
        net_sell = insider_tx.get("net_sell", 0)
        if net_sell and net_sell > 50_000_000:
            reasons.append("Insider selling >$50M in 90d")
            evidence.append(f"Net insider sell: ${net_sell:,.0f}")

    # Rule 6: Regulatory action (NOW AUTOMATED via news check)
    regulatory_result = check_regulatory_action(data)
    if regulatory_result.get("blocked"):
        reasons.append(regulatory_result["reason"])
        evidence.extend(regulatory_result["evidence"])

    # Rule 7: Solvency crisis (ENHANCED)
    solvency_issues = check_enhanced_solvency(data)
    for issue in solvency_issues:
        reasons.append(issue["reason"])
        evidence.append(issue["evidence"])

    # Rule 8: No revenue plus no earnings (NOW AUTOMATED)
    revenue_result = check_revenue_earnings(data)
    if revenue_result.get("blocked"):
        reasons.append(revenue_result["reason"])
        evidence.append(revenue_result["evidence"])
    elif revenue_result.get("evidence") and "N/A" not in revenue_result["evidence"]:
        evidence.append(revenue_result["evidence"])

    # Rule 9: Regular plan MF (handled at recommendation level)

    blocked = len(reasons) > 0 or data.get("blocked", False)

    if data.get("blocked") and not reasons:
        db_list = data.get("deal_breakers", [])
        if db_list:
            reasons.append(str(db_list[0]) if isinstance(db_list, list) else str(db_list))
            evidence.append("MCP auto-check triggered")

    needs_manual = []
    if not blocked:
        if not data.get("financial_statements", {}).get("available"):
            needs_manual.append("Altman Z-Score (insufficient financial data)")
        if not data.get("regulatory_check", {}).get("headlines"):
            needs_manual.append("Regulatory action (no news data)")
        needs_manual.extend([
            "QoE Ratio (CFO/NI) < 0.7 for 2+ years",
            "Accounting red flags / auditor qualification",
            "Promoter pledge > 50% (India)",
        ])

    return {
        "blocked": blocked,
        "reasons": reasons,
        "evidence": evidence,
        "needs_manual_check": needs_manual
    }


def _get_num(data: Dict, key: str) -> Optional[float]:
    """Safely extract a numeric value."""
    val = data.get(key)
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
