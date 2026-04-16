import time
import yfinance as yf


def _classify_market(info: dict) -> tuple[str, str]:
    """Return (market, currency) from ticker info."""
    exchange = info.get("exchange", "")
    currency = info.get("currency", "USD")
    if exchange in ("NSI", "NSE", "BSE", "BOM"):
        return "India", currency
    if exchange in ("TOR", "TSX", "CVE", "NEO"):
        return "Canada", currency
    return "US", currency


def _build_resolved(input_query: str, symbol: str, info: dict) -> dict:
    market, currency = _classify_market(info)
    return {
        "input": input_query,
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName", symbol),
        "exchange": info.get("exchange", ""),
        "market": market,
        "currency": currency,
    }


def _try_ticker(symbol: str) -> dict | None:
    """Return info dict if ticker is valid (has longName or shortName), else None."""
    try:
        info = yf.Ticker(symbol).info
        if info.get("longName") or info.get("shortName"):
            return info
    except Exception:
        pass
    return None


def _try_search(query: str) -> list[dict]:
    """Use yf.Search if available. Returns list of quote dicts."""
    try:
        results = yf.Search(query).quotes
        return results if results else []
    except AttributeError:
        # yf.Search not available in this yfinance version
        return []
    except Exception:
        return []


def _resolve_single(query: str) -> dict:
    """
    Resolve one query to a ticker. Returns dict with one of:
    - {"resolved": {...}}
    - {"ambiguous": {"input": ..., "candidates": [...], "reason": ...}}
    - {"failed": {"input": ..., "reason": ...}}
    """
    q = query.strip()

    # Step 1: direct match
    info = _try_ticker(q)
    if info:
        return {"resolved": _build_resolved(q, q, info)}

    # Step 2: .NS suffix (India NSE)
    info = _try_ticker(q + ".NS")
    if info:
        return {"resolved": _build_resolved(q, q + ".NS", info)}

    # Step 3: .TO suffix (Canada TSX)
    info = _try_ticker(q + ".TO")
    if info:
        return {"resolved": _build_resolved(q, q + ".TO", info)}

    # Step 4: yf.Search
    quotes = _try_search(q)
    if quotes:
        if len(quotes) == 1:
            sym = quotes[0].get("symbol", q)
            info = _try_ticker(sym)
            if info:
                return {"resolved": _build_resolved(q, sym, info)}
        elif len(quotes) > 1:
            candidates = [r.get("symbol", "") for r in quotes if r.get("symbol")]
            return {
                "ambiguous": {
                    "input": q,
                    "candidates": candidates[:5],
                    "reason": f"Multiple matches found. Ask user to clarify from: {candidates[:5]}",
                }
            }

    # Step 5: fallback suffixes
    for suffix in [".BO", ".L"]:
        time.sleep(0.1)
        info = _try_ticker(q + suffix)
        if info:
            return {"resolved": _build_resolved(q, q + suffix, info)}

    # Step 6: failed
    return {"failed": {"input": q, "reason": f"No match found for '{q}' on Yahoo Finance."}}


def resolve_tickers_impl(queries: list[str]) -> dict:
    resolved = []
    ambiguous = []
    failed = []

    for query in queries:
        result = _resolve_single(query)
        if "resolved" in result:
            resolved.append(result["resolved"])
        elif "ambiguous" in result:
            ambiguous.append(result["ambiguous"])
        else:
            failed.append(result["failed"])
        time.sleep(0.2)  # avoid rate limiting between queries

    return {
        "resolved": resolved,
        "ambiguous": ambiguous,
        "failed": failed,
    }
