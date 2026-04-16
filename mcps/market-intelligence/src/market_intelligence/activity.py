import yfinance as yf


def _df_to_records(df, limit=10) -> list[dict]:
    """Convert a DataFrame to a list of dicts, capping at limit rows."""
    if df is None or df.empty:
        return []
    df = df.head(limit).copy()
    # Convert index to column if it's named (e.g. GradeDate)
    if df.index.name:
        df = df.reset_index()
    # Stringify non-serializable types
    for col in df.columns:
        df[col] = df[col].astype(str).where(df[col].apply(lambda x: not hasattr(x, 'isoformat')), df[col].apply(lambda x: str(x)))
    return df.to_dict(orient="records")


def get_institutional_activity_impl(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
    except Exception as e:
        return {"symbol": symbol, "error": f"Failed to fetch data: {e}"}

    exchange = info.get("exchange", "")
    is_indian = exchange in ("NSI", "NSE", "BSE", "BOM")

    result: dict = {"symbol": symbol, "market": "India" if is_indian else "US/Canada/Other"}

    # --- Insider Transactions ---
    try:
        df = ticker.insider_transactions
        records = _df_to_records(df, limit=15)
        result["insider_transactions"] = records if records else None
        result["insider_transactions_note"] = None if records else (
            "Not available for Indian stocks via Yahoo Finance." if is_indian else "No insider transaction data found."
        )
    except Exception as e:
        result["insider_transactions"] = None
        result["insider_transactions_note"] = f"Error: {e}"

    # --- Institutional Holders ---
    try:
        df = ticker.institutional_holders
        records = _df_to_records(df, limit=15)
        result["institutional_holders"] = records if records else None
        result["institutional_holders_note"] = None if records else (
            "Not available for Indian stocks via Yahoo Finance. Use get_fii_dii_flows for India institutional data." if is_indian
            else "No institutional holder data found."
        )
    except Exception as e:
        result["institutional_holders"] = None
        result["institutional_holders_note"] = f"Error: {e}"

    # --- Mutual Fund Holders ---
    try:
        df = ticker.mutualfund_holders
        records = _df_to_records(df, limit=10)
        result["mutualfund_holders"] = records if records else None
    except Exception:
        result["mutualfund_holders"] = None

    # --- Analyst Upgrades / Downgrades ---
    try:
        df = ticker.upgrades_downgrades
        records = _df_to_records(df, limit=10)
        result["upgrades_downgrades"] = records if records else None
        result["upgrades_downgrades_note"] = None if records else (
            "Not available for Indian stocks via Yahoo Finance." if is_indian else "No upgrades/downgrades data found."
        )
    except Exception as e:
        result["upgrades_downgrades"] = None
        result["upgrades_downgrades_note"] = f"Error: {e}"

    # --- Earnings Calendar ---
    try:
        cal = ticker.calendar
        if cal and isinstance(cal, dict):
            cleaned = {}
            for k, v in cal.items():
                if isinstance(v, list):
                    cleaned[k] = [str(i) for i in v]
                else:
                    cleaned[k] = str(v)
            result["earnings_calendar"] = cleaned
        else:
            result["earnings_calendar"] = None
    except Exception as e:
        result["earnings_calendar"] = None
        result["earnings_calendar_note"] = f"Error: {e}"

    # --- Major Holders summary ---
    try:
        df = ticker.major_holders
        records = _df_to_records(df, limit=10)
        result["major_holders_summary"] = records if records else None
    except Exception:
        result["major_holders_summary"] = None

    return result
