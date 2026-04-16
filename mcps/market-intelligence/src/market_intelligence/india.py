import yfinance as yf


def _pe_to_zone(pe: float | None) -> dict:
    if pe is None:
        return {"zone": "Unknown", "guidance": "P/E data unavailable"}
    if pe < 18:
        return {"zone": "Excellent", "guidance": "Market is significantly undervalued. Strong buying opportunity."}
    if pe < 22:
        return {"zone": "Good", "guidance": "Market is fairly valued. Good entry conditions."}
    if pe < 25:
        return {"zone": "Fair", "guidance": "Market is fairly priced. Selective stock picking warranted."}
    if pe < 28:
        return {"zone": "Expensive", "guidance": "Market is expensive. Caution advised; prefer quality stocks."}
    return {"zone": "Bubble", "guidance": "Market in bubble territory. High risk; consider reducing exposure."}


def _fii_dii_signal(fii_net: float, dii_net: float) -> str:
    if fii_net > 0 and dii_net > 0:
        return "Strong institutional confidence — both FII and DII are buying."
    if fii_net > 0 and dii_net < 0:
        return "FII buying while DII selling — mixed signals, watch for divergence."
    if fii_net < 0 and dii_net > 0:
        return "DII absorbing FII selling — resilient but under pressure."
    return "Caution — both FII and DII are selling. Potential correction ahead."


def get_fii_dii_flows_impl(days: int = 20) -> dict:
    try:
        import nsepython
        raw = nsepython.fii_dii()

        if raw is None or (hasattr(raw, "__len__") and len(raw) == 0):
            return {"error": "NSE data temporarily unavailable. Retry in 5 minutes."}

        # nsepython returns a DataFrame or list of dicts
        import pandas as pd
        if not isinstance(raw, pd.DataFrame):
            df = pd.DataFrame(raw)
        else:
            df = raw

        df = df.head(days)

        # Normalize column names (nsepython may vary)
        col_map = {}
        for col in df.columns:
            cl = col.lower().replace(" ", "_")
            col_map[col] = cl
        df = df.rename(columns=col_map)

        daily = []
        for _, row in df.iterrows():
            entry = {}
            for col in df.columns:
                try:
                    entry[col] = float(row[col]) if str(row[col]).replace(".", "").replace("-", "").isdigit() else str(row[col])
                except Exception:
                    entry[col] = str(row[col])
            daily.append(entry)

        # Try to compute rolling totals from fii_net / dii_net columns
        fii_col = next((c for c in df.columns if "fii" in c and "net" in c), None)
        dii_col = next((c for c in df.columns if "dii" in c and "net" in c), None)

        summary = {}
        signal = "Insufficient data to determine signal."
        if fii_col and dii_col:
            try:
                fii_total = float(df[fii_col].astype(str).str.replace(",", "").apply(pd.to_numeric, errors="coerce").sum())
                dii_total = float(df[dii_col].astype(str).str.replace(",", "").apply(pd.to_numeric, errors="coerce").sum())
                summary = {
                    "fii_net_total": round(fii_total, 2),
                    "dii_net_total": round(dii_total, 2),
                    "period_days": days,
                }
                signal = _fii_dii_signal(fii_total, dii_total)
            except Exception:
                pass

        return {
            "daily": daily,
            "summary": summary,
            "signal": signal,
        }

    except ImportError:
        return {"error": "nsepython not installed. Run: pip install nsepython"}
    except Exception as e:
        return {"error": f"NSE data temporarily unavailable. Retry in 5 minutes. Detail: {e}"}


def get_nifty_valuation_impl() -> dict:
    # Try nsetools first
    try:
        from nsetools import Nse
        nse = Nse()
        data = nse.get_index_quote("NIFTY 50")
        if data:
            pe = data.get("pe") or data.get("pE")
            try:
                pe_val = float(pe) if pe else None
            except Exception:
                pe_val = None
            zone_info = _pe_to_zone(pe_val)
            return {
                "source": "nsetools",
                "pe": pe_val,
                "pb": data.get("pb") or data.get("pB"),
                "dividend_yield": data.get("dy") or data.get("dY"),
                "year_high": data.get("yearHigh"),
                "year_low": data.get("yearLow"),
                "last_price": data.get("last") or data.get("lastPrice"),
                "advances": data.get("advances"),
                "declines": data.get("declines"),
                "valuation_zone": zone_info["zone"],
                "guidance": zone_info["guidance"],
            }
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: yfinance
    try:
        info = yf.Ticker("^NSEI").info
        if info:
            return {
                "source": "yfinance_fallback",
                "last_price": info.get("previousClose") or info.get("regularMarketPrice"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "note": "P/E and P/B not available via yfinance for index. Use nsetools for full valuation data.",
            }
    except Exception as e:
        return {"error": f"Both nsetools and yfinance fallback failed: {e}"}

    return {"error": "Could not fetch Nifty 50 valuation data."}
