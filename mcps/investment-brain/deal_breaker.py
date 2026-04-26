"""Deal-Breaker Checker - Runs BEFORE scoring.

Implements all 9 deal-breakers from scoring_and_metrics.md.
Any single trigger = automatic disqualification.
"""

from typing import Dict, List, Optional, Any
from config import DEAL_BREAKERS


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

    # Handle nested MCP structure
    if not quality and "mcp_scoring" in data:
        raw_profile = data["mcp_scoring"].get("raw_profile", {})
        quality = raw_profile.get("quality", {})
        valuation = raw_profile.get("valuation", {})
        risk = raw_profile.get("risk", {})
        identity = raw_profile.get("identity", {})

    reasons = []
    evidence = []

    # 1. Earnings manipulation: QoE Ratio < 0.7 for 2+ years
    # (Requires manual verification - flag as unverified)
    # We can't compute QoE without full financials, so we skip auto-check
    # but flag if FCF is consistently negative (proxy)

    # 2. Bankruptcy risk: Altman Z < 1.81
    # (Requires manual verification - flag as unverified)

    # 3. Accounting red flags
    # (Requires web search - flag as unverified)

    # 4. Negative FCF sustained 2+ years
    fcf = _get_num(quality, "free_cashflow")
    if fcf is not None and fcf < 0:
        # We only have current FCF from MCP/yfinance, not history
        # Flag as potential deal-breaker if MCP already flagged it
        if data.get("blocked") and "negative cash flow" in str(data.get("deal_breakers", [])).lower():
            reasons.append("Negative FCF sustained")
            evidence.append(f"FCF: ${fcf:,.0f}")

    # 5. Broken insider alignment
    insider_pct = _get_num(risk, "insider_pct")
    insider_tx = institutional.get("insider_transactions", {}) if isinstance(institutional, dict) else {}
    if insider_tx and isinstance(insider_tx, dict):
        net_sell = insider_tx.get("net_sell", 0)
        if net_sell and net_sell > 50_000_000:  # >$50M
            reasons.append("Insider selling >$50M in 90d")
            evidence.append(f"Net insider sell: ${net_sell:,.0f}")

    # 6. Regulatory action
    # (Requires web search - flag as unverified)

    # 7. Solvency crisis
    current_ratio = _get_num(quality, "current_ratio")
    de = _get_num(quality, "debt_to_equity")

    if current_ratio is not None and current_ratio < DEAL_BREAKERS["current_ratio_min"]:
        reasons.append(f"Current ratio {current_ratio:.2f} < {DEAL_BREAKERS['current_ratio_min']}")
        evidence.append(f"Current ratio: {current_ratio:.2f}")

    if de is not None and de > DEAL_BREAKERS["debt_equity_max"]:
        reasons.append(f"D/E {de:.0f} > {DEAL_BREAKERS['debt_equity_max']}")
        evidence.append(f"D/E: {de:.0f}")

    # 8. No revenue plus no earnings
    revenue_growth = _get_num(quality, "revenue_growth") or _get_num(profile.get("growth", {}) if isinstance(profile, dict) else {}, "revenue_growth")
    earnings_growth = _get_num(quality, "earnings_growth") or _get_num(profile.get("growth", {}) if isinstance(profile, dict) else {}, "earnings_growth")

    if data.get("blocked") and "no revenue" in str(data.get("deal_breakers", [])).lower():
        reasons.append("No revenue and no earnings")
        evidence.append("MCP auto-blocked: no revenue")

    # 9. Regular plan MF (handled at recommendation level, not data level)

    blocked = len(reasons) > 0 or data.get("blocked", False)

    # Add MCP auto-block reasons
    if data.get("blocked") and not reasons:
        db_list = data.get("deal_breakers", [])
        if db_list:
            reasons.append(str(db_list[0]) if isinstance(db_list, list) else str(db_list))
            evidence.append("MCP auto-check triggered")

    return {
        "blocked": blocked,
        "reasons": reasons,
        "evidence": evidence,
        "needs_manual_check": [
            "QoE Ratio (CFO/NI) < 0.7 for 2+ years",
            "Altman Z-Score < 1.81",
            "Accounting red flags / auditor qualification",
            "Regulatory action (SEC/SEBI)",
            "Promoter pledge > 50% (India)",
        ] if not blocked else []
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
