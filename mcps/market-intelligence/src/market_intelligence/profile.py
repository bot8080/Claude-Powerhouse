import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf


def _safe(info: dict, key: str, default=None):
    val = info.get(key, default)
    return val if val not in (None, "N/A", "", float("inf"), float("-inf")) else default


def _earnings_quality(ticker) -> dict:
    """Compute earnings quality metrics: FCF/NI ratio and accruals ratio.
    Based on Sloan (1996) accruals anomaly research. High accruals = lower earnings quality.
    """
    try:
        cf = ticker.cashflow
        bs = ticker.balance_sheet
        inc = ticker.income_stmt
    except Exception:
        return {"error": "Could not fetch financial statements"}

    def _get_row(df, *keys):
        """Try multiple row name variants (yfinance naming varies)."""
        if df is None or df.empty:
            return None
        for k in keys:
            if k in df.index:
                val = df.loc[k].iloc[0]  # most recent year
                try:
                    return float(val)
                except Exception:
                    continue
        return None

    cfo = _get_row(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = _get_row(cf, "Capital Expenditure", "Capital Expenditures")
    net_income = _get_row(inc, "Net Income", "Net Income Common Stockholders")
    total_assets_curr = _get_row(bs, "Total Assets")
    total_assets_prev = None
    try:
        if bs is not None and not bs.empty and bs.shape[1] >= 2:
            for k in ("Total Assets",):
                if k in bs.index:
                    total_assets_prev = float(bs.loc[k].iloc[1])
                    break
    except Exception:
        pass

    result: dict = {}

    # FCF = CFO - CapEx
    fcf = None
    if cfo is not None and capex is not None:
        fcf = cfo - abs(capex)  # capex is often negative in yfinance
    elif cfo is not None:
        fcf = cfo  # fallback if capex not available

    result["operating_cash_flow"] = round(cfo, 0) if cfo is not None else None
    result["capital_expenditure"] = round(capex, 0) if capex is not None else None
    result["free_cash_flow_computed"] = round(fcf, 0) if fcf is not None else None
    result["net_income_stmt"] = round(net_income, 0) if net_income is not None else None

    # FCF / Net Income ratio
    if fcf is not None and net_income and net_income != 0:
        ratio = round(fcf / net_income, 3)
        result["fcf_to_net_income_ratio"] = ratio
        if ratio > 1.0:
            result["earnings_quality"] = "excellent"
            result["earnings_quality_note"] = f"FCF/NI={ratio:.2f} — cash exceeds reported earnings, high quality"
        elif ratio >= 0.8:
            result["earnings_quality"] = "good"
            result["earnings_quality_note"] = f"FCF/NI={ratio:.2f} — earnings well backed by cash"
        elif ratio >= 0.5:
            result["earnings_quality"] = "warning"
            result["earnings_quality_note"] = f"FCF/NI={ratio:.2f} — potential accounting inflation"
        elif ratio >= 0:
            result["earnings_quality"] = "poor"
            result["earnings_quality_note"] = f"FCF/NI={ratio:.2f} — earnings heavily reliant on non-cash items"
        else:
            result["earnings_quality"] = "red_flag"
            result["earnings_quality_note"] = f"FCF/NI={ratio:.2f} — negative FCF with positive NI: major red flag"
    else:
        result["fcf_to_net_income_ratio"] = None
        result["earnings_quality"] = "unavailable"
        result["earnings_quality_note"] = "Could not compute — missing CFO or NI data"

    # Accruals Ratio = (NI - CFO) / Average Total Assets
    if net_income is not None and cfo is not None and total_assets_curr is not None:
        avg_assets = (
            (total_assets_curr + total_assets_prev) / 2
            if total_assets_prev
            else total_assets_curr
        )
        accruals_ratio = round((net_income - cfo) / avg_assets, 4) if avg_assets else None
        result["accruals_ratio"] = accruals_ratio
        if accruals_ratio is not None:
            if accruals_ratio < -0.05:
                result["accruals_note"] = "Negative accruals — cash earnings exceed reported: strong quality signal"
            elif accruals_ratio < 0.05:
                result["accruals_note"] = "Near-zero accruals — balanced earnings quality"
            elif accruals_ratio < 0.1:
                result["accruals_note"] = "Moderate accruals — some accounting adjustments in earnings"
            else:
                result["accruals_note"] = "High accruals — significant portion of earnings from non-cash adjustments"
    else:
        result["accruals_ratio"] = None
        result["accruals_note"] = "Could not compute — missing financial statement data"

    return result


def get_full_profile_impl(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
    except Exception as e:
        return {"symbol": symbol, "error": f"Failed to fetch data: {e}"}

    if not info or not (info.get("longName") or info.get("shortName")):
        return {"symbol": symbol, "error": "No data found. Check the ticker symbol."}

    return {
        "symbol": symbol,
        "identity": {
            "name": _safe(info, "longName") or _safe(info, "shortName"),
            "sector": _safe(info, "sector"),
            "industry": _safe(info, "industry"),
            "exchange": _safe(info, "exchange"),
            "currency": _safe(info, "currency"),
            "market_cap": _safe(info, "marketCap"),
            "employees": _safe(info, "fullTimeEmployees"),
            "country": _safe(info, "country"),
            "website": _safe(info, "website"),
        },
        "price": {
            "current": _safe(info, "currentPrice") or _safe(info, "previousClose"),
            "open": _safe(info, "open"),
            "day_high": _safe(info, "dayHigh"),
            "day_low": _safe(info, "dayLow"),
            "52w_high": _safe(info, "fiftyTwoWeekHigh"),
            "52w_low": _safe(info, "fiftyTwoWeekLow"),
            "52w_change_pct": _safe(info, "52WeekChange"),
            "vs_sp500_52w_pct": _safe(info, "SandP52WeekChange"),
            "all_time_high": _safe(info, "allTimeHigh"),
            "all_time_low": _safe(info, "allTimeLow"),
            "sma_50": _safe(info, "fiftyDayAverage"),
            "sma_200": _safe(info, "twoHundredDayAverage"),
            "volume": _safe(info, "volume"),
            "avg_volume": _safe(info, "averageVolume"),
        },
        "valuation": {
            "pe_trailing": _safe(info, "trailingPE"),
            "pe_forward": _safe(info, "forwardPE"),
            "price_to_book": _safe(info, "priceToBook"),
            "price_to_sales": _safe(info, "priceToSalesTrailing12Months"),
            "ev_to_ebitda": _safe(info, "enterpriseToEbitda"),
            "ev_to_revenue": _safe(info, "enterpriseToRevenue"),
            "peg_ratio": _safe(info, "pegRatio") or _safe(info, "trailingPegRatio"),
            "enterprise_value": _safe(info, "enterpriseValue"),
            "book_value": _safe(info, "bookValue"),
        },
        "quality": {
            "roe": _safe(info, "returnOnEquity"),
            "roa": _safe(info, "returnOnAssets"),
            "profit_margin": _safe(info, "profitMargins"),
            "operating_margin": _safe(info, "operatingMargins"),
            "gross_margin": _safe(info, "grossMargins"),
            "gross_profits": _safe(info, "grossProfits"),
            "debt_to_equity": _safe(info, "debtToEquity"),
            "current_ratio": _safe(info, "currentRatio"),
            "quick_ratio": _safe(info, "quickRatio"),
            "total_cash": _safe(info, "totalCash"),
            "total_cash_per_share": _safe(info, "totalCashPerShare"),
            "total_debt": _safe(info, "totalDebt"),
            "free_cashflow": _safe(info, "freeCashflow"),
            "operating_cashflow": _safe(info, "operatingCashflow"),
        },
        "growth": {
            "revenue": _safe(info, "totalRevenue"),
            "revenue_growth": _safe(info, "revenueGrowth"),
            "earnings_growth": _safe(info, "earningsGrowth"),
            "earnings_quarterly_growth": _safe(info, "earningsQuarterlyGrowth"),
            "ebitda": _safe(info, "ebitda"),
            "ebitda_margin": _safe(info, "ebitdaMargins"),
            "eps_trailing": _safe(info, "trailingEps"),
            "eps_forward": _safe(info, "forwardEps"),
            "revenue_per_share": _safe(info, "revenuePerShare"),
            "net_income": _safe(info, "netIncomeToCommon"),
        },
        "analyst": {
            "target_mean": _safe(info, "targetMeanPrice"),
            "target_median": _safe(info, "targetMedianPrice"),
            "target_high": _safe(info, "targetHighPrice"),
            "target_low": _safe(info, "targetLowPrice"),
            "recommendation": _safe(info, "recommendationKey"),
            "recommendation_mean": _safe(info, "recommendationMean"),
            "analyst_count": _safe(info, "numberOfAnalystOpinions"),
        },
        "risk": {
            "beta": _safe(info, "beta"),
            "insider_pct": _safe(info, "heldPercentInsiders"),
            "institution_pct": _safe(info, "heldPercentInstitutions"),
            "short_ratio": _safe(info, "shortRatio"),
            "shares_short": _safe(info, "sharesShort"),
            "short_pct_of_float": _safe(info, "shortPercentOfFloat"),
            "float_shares": _safe(info, "floatShares"),
            "shares_outstanding": _safe(info, "sharesOutstanding"),
            "audit_risk": _safe(info, "auditRisk"),
            "board_risk": _safe(info, "boardRisk"),
            "overall_risk": _safe(info, "overallRisk"),
        },
        "dividends": {
            "yield": _safe(info, "dividendYield"),
            "rate": _safe(info, "dividendRate"),
            "five_year_avg_yield": _safe(info, "fiveYearAvgDividendYield"),
            "payout_ratio": _safe(info, "payoutRatio"),
            "ex_date": _safe(info, "exDividendDate"),
        },
        "description": _safe(info, "longBusinessSummary"),
        "earnings_quality": _earnings_quality(ticker),
    }


def get_batch_profiles_impl(symbols: list[str]) -> dict:
    profiles = []
    errors = []

    def fetch_one(sym: str) -> dict:
        time.sleep(0.3)
        return get_full_profile_impl(sym)

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_sym = {executor.submit(fetch_one, sym): sym for sym in symbols}
        for future in as_completed(future_to_sym):
            result = future.result()
            if "error" in result:
                errors.append(result)
            else:
                profiles.append(result)

    return {
        "profiles": profiles,
        "errors": errors,
        "count": len(symbols),
        "success_count": len(profiles),
        "error_count": len(errors),
    }
