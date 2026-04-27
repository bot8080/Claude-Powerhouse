"""Data Fetcher - Primary: MCP, Fallback: yfinance + free APIs.

Handles US, CA, and IN markets. Falls back gracefully when MCP is unavailable.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import MCP_SERVER_CMD, DEFAULT_MARKET
from mcp_bridge import MCPDataFetcher


class DataFetcher:
    """Unified data fetcher with MCP primary and yfinance fallback."""

    def __init__(self):
        self.mcp: Optional[MCPDataFetcher] = None
        self._yf_available = False
        self._try_import_yfinance()

        if MCP_SERVER_CMD:
            self.mcp = MCPDataFetcher(MCP_SERVER_CMD)
            if not self.mcp.connect():
                print("[WARN] MCP connection failed. Using yfinance fallback.")
                self.mcp = None
        else:
            print("[INFO] MCP_SERVER_CMD not set. Using yfinance only.")

    def _try_import_yfinance(self):
        """Try to import yfinance for fallback."""
        try:
            import yfinance as yf
            self._yf = yf
            self._yf_available = True
        except ImportError:
            print("[WARN] yfinance not installed. Install with: pip install yfinance")
            self._yf_available = False

    def close(self):
        if self.mcp:
            self.mcp.disconnect()

    def resolve_ticker(self, query: str) -> Optional[str]:
        """Resolve a company name or ticker to a canonical symbol."""
        if self.mcp:
            results = self.mcp.resolve_tickers([query])
            if results and len(results) > 0:
                return results[0].get("symbol")
        # Fallback: assume query is already a ticker
        return query.upper()

    def get_stock_data(self, symbol: str, market: str = DEFAULT_MARKET) -> Optional[Dict]:
        """Fetch complete stock data: profile + technicals + institutional."""
        data = {"symbol": symbol, "market": market, "timestamp": datetime.now().isoformat()}

        # Try MCP first
        if self.mcp:
            scoring = self.mcp.get_scoring_data(symbol)
            if scoring:
                data["mcp_scoring"] = scoring
                data["profile"] = scoring.get("raw_profile", {})
                data["technicals"] = scoring.get("raw_technicals", {})
                data["blocked"] = scoring.get("blocked", False)
                data["deal_breakers"] = scoring.get("deal_breakers", [])

            inst = self.mcp.get_institutional_activity(symbol)
            if inst:
                data["institutional"] = inst

        # yfinance fallback / enrichment
        if self._yf_available:
            self._enrich_with_yfinance(data, symbol)

            # Fetch financial statements for Altman Z calculation
            financials = self.get_financial_statements(symbol)
            if financials.get("available"):
                data["financial_statements"] = financials

            # Check regulatory news
            company_name = data.get("profile", {}).get("identity", {}).get("name", "")
            regulatory = self.check_regulatory_news(symbol, company_name)
            if regulatory.get("headlines"):
                data["regulatory_check"] = regulatory

        return data if data.get("profile") or data.get("mcp_scoring") else None

    def _enrich_with_yfinance(self, data: Dict, symbol: str):
        """Add yfinance data as fallback or enrichment."""
        try:
            ticker = self._yf.Ticker(symbol)
            info = ticker.info
            if not info:
                return

            # Build profile from yfinance if MCP missing
            if not data.get("profile"):
                data["profile"] = {
                    "identity": {
                        "symbol": symbol,
                        "name": info.get("longName", info.get("shortName", symbol)),
                        "sector": info.get("sector", "Unknown"),
                        "industry": info.get("industry", ""),
                        "market_cap": info.get("marketCap"),
                    },
                    "valuation": {
                        "pe_trailing": info.get("trailingPE"),
                        "pe_forward": info.get("forwardPE"),
                        "peg_ratio": info.get("pegRatio"),
                        "pb_ratio": info.get("priceToBook"),
                        "ev_ebitda": info.get("enterpriseToEbitda"),
                    },
                    "quality": {
                        "roe": info.get("returnOnEquity"),
                        "profit_margin": info.get("profitMargins"),
                        "operating_margin": info.get("operatingMargins"),
                        "debt_to_equity": info.get("debtToEquity"),
                        "current_ratio": info.get("currentRatio"),
                        "free_cashflow": info.get("freeCashflow"),
                    },
                    "growth": {
                        "revenue_growth": info.get("revenueGrowth"),
                        "earnings_growth": info.get("earningsGrowth"),
                    },
                    "dividends": {
                        "yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
                        "payout_ratio": info.get("payoutRatio", 0) * 100 if info.get("payoutRatio") else 0,
                    },
                    "analyst": {
                        "target_mean": info.get("targetMeanPrice"),
                        "target_high": info.get("targetHighPrice"),
                        "target_low": info.get("targetLowPrice"),
                        "recommendation": info.get("recommendationKey", ""),
                        "num_analysts": info.get("numberOfAnalystOpinions", 0),
                    },
                    "risk": {
                        "beta": info.get("beta"),
                        "overall_risk": info.get("overallRisk"),
                        "audit_risk": info.get("auditRisk"),
                        "board_risk": info.get("boardRisk"),
                        "insider_pct": info.get("heldPercentInsiders", 0) * 100 if info.get("heldPercentInsiders") else 0,
                        "institution_pct": info.get("heldPercentInstitutions", 0) * 100 if info.get("heldPercentInstitutions") else 0,
                        "short_ratio": info.get("shortRatio"),
                        "short_pct_float": info.get("shortPercentOfFloat", 0) * 100 if info.get("shortPercentOfFloat") else 0,
                    },
                    "price": {
                        "current": info.get("currentPrice", info.get("regularMarketPrice")),
                        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                        "fifty_day_average": info.get("fiftyDayAverage"),
                        "two_hundred_day_average": info.get("twoHundredDayAverage"),
                    }
                }

            # Technicals from yfinance history
            if not data.get("technicals"):
                hist = ticker.history(period="1y")
                if not hist.empty:
                    data["technicals"] = self._calc_technicals_from_history(hist)

            # Price update
            if data.get("profile") and not data["profile"].get("price", {}).get("current"):
                if info.get("currentPrice"):
                    data["profile"]["price"] = data["profile"].get("price", {})
                    data["profile"]["price"]["current"] = info["currentPrice"]

        except Exception as e:
            print(f"[yfinance] Error fetching {symbol}: {e}")

    def _calc_technicals_from_history(self, hist) -> Dict:
        """Calculate technical indicators from price history."""
        import pandas as pd
        close = hist["Close"]
        volume = hist["Volume"]

        # SMAs
        sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else close.mean()
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else close.mean()
        current = close.iloc[-1]

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        macd_bullish = macd_line.iloc[-1] > signal_line.iloc[-1]

        # Bollinger
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = sma20 + 2 * std20
        lower = sma20 - 2 * std20
        bb_pct_b = (current - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) if upper.iloc[-1] != lower.iloc[-1] else 0.5

        # ATR
        high_low = hist["High"] - hist["Low"]
        high_close = (hist["High"] - close.shift()).abs()
        low_close = (hist["Low"] - close.shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        atr_pct = (atr / current) * 100 if current else 0

        # ADX (simplified)
        adx = 20  # placeholder

        # Volume
        vol_avg = volume.rolling(20).mean().iloc[-1]
        vol_ratio = volume.iloc[-1] / vol_avg if vol_avg else 1

        # OBV
        obv = (volume * (close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)))).cumsum().iloc[-1]
        obv_trend = "rising" if obv > 0 else "falling"

        # MFI (simplified)
        mfi = 50  # placeholder

        return {
            "trend": {
                "above_50dma": current > sma50,
                "above_200dma": current > sma200,
                "price_vs_200dma_pct": ((current - sma200) / sma200) * 100 if sma200 else 0,
                "golden_cross": sma50 > sma200 and close.rolling(50).mean().iloc[-2] <= close.rolling(200).mean().iloc[-2] if len(close) > 200 else False,
                "death_cross": sma50 < sma200 and close.rolling(50).mean().iloc[-2] >= close.rolling(200).mean().iloc[-2] if len(close) > 200 else False,
            },
            "momentum": {
                "rsi_14": round(rsi, 1),
                "rsi_zone": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral",
                "macd_bullish": macd_bullish,
            },
            "volatility": {
                "atr_pct": round(atr_pct, 2),
                "bb_pct_b": round(bb_pct_b, 3),
                "bb_bandwidth": round(((upper.iloc[-1] - lower.iloc[-1]) / sma20.iloc[-1]) * 100, 2) if sma20.iloc[-1] else 0,
            },
            "strength": {
                "adx_14": adx,
                "trend_direction": "bullish" if current > sma200 else "bearish",
            },
            "volume": {
                "obv_trend": obv_trend,
                "mfi_14": mfi,
                "mfi_zone": "neutral",
                "volume_vs_avg_20d": round(vol_ratio, 2),
            },
            "signals": {
                "overall": "bullish" if current > sma200 and macd_bullish else "bearish" if current < sma200 else "neutral",
                "suggested_stop_loss": round(current * 0.9, 2),
            }
        }

    def get_batch_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch data for multiple tickers."""
        results = []
        for sym in symbols:
            data = self.get_stock_data(sym)
            if data:
                results.append(data)
        return results

    def get_financial_statements(self, symbol: str) -> Dict:
        """Fetch balance sheet and income statement for Altman Z calculation.

        Returns:
            Dict with balance_sheet, income_statement, and derived metrics
        """
        result = {
            "balance_sheet": {},
            "income_statement": {},
            "derived": {},
            "available": False,
        }

        if not self._yf_available:
            return result

        try:
            ticker = self._yf.Ticker(symbol)

            # Get balance sheet (most recent annual)
            bs = ticker.balance_sheet
            if bs is not None and not bs.empty:
                latest = bs.iloc[:, 0]  # Most recent period

                result["balance_sheet"] = {
                    "total_assets": latest.get("Total Assets"),
                    "total_liabilities": latest.get("Total Liabilities"),
                    "total_equity": latest.get("Total Stockholder Equity"),
                    "working_capital": latest.get("Working Capital"),
                    "retained_earnings": latest.get("Retained Earnings"),
                    "current_assets": latest.get("Current Assets"),
                    "current_liabilities": latest.get("Current Liabilities"),
                    "cash": latest.get("Cash And Cash Equivalents"),
                    "marketable_securities": latest.get("Marketable Securities"),
                }

            # Get income statement (most recent annual)
            isf = ticker.income_stmt
            if isf is not None and not isf.empty:
                latest = isf.iloc[:, 0]

                result["income_statement"] = {
                    "revenue": latest.get("Total Revenue"),
                    "ebit": latest.get("Operating Income"),
                    "net_income": latest.get("Net Income"),
                    "interest_expense": latest.get("Interest Expense"),
                    "ebitda": latest.get("Operating Income"),  # Approximate if EBITDA not available
                }

            # Calculate derived metrics for Altman Z
            bs_data = result["balance_sheet"]
            is_data = result["income_statement"]

            ta = bs_data.get("total_assets")
            tl = bs_data.get("total_liabilities")
            wc = bs_data.get("working_capital")
            re = bs_data.get("retained_earnings")
            ebit = is_data.get("ebit")
            equity = bs_data.get("total_equity")
            revenue = is_data.get("revenue")
            interest = is_data.get("interest_expense")

            if ta and ta > 0:
                result["derived"] = {
                    "working_capital_to_assets": (wc / ta) if wc else None,
                    "retained_earnings_to_assets": (re / ta) if re else None,
                    "ebit_to_assets": (ebit / ta) if ebit else None,
                    "equity_to_liabilities": (equity / tl) if (equity and tl) else None,
                    "sales_to_assets": (revenue / ta) if revenue else None,
                    "interest_coverage": (ebit / interest) if (ebit and interest and interest != 0) else None,
                }

            result["available"] = True

        except Exception as e:
            print(f"[financials] Error fetching for {symbol}: {e}")

        return result

    def check_regulatory_news(self, symbol: str, company_name: str) -> Dict:
        """Check for regulatory actions via news search.

        Returns:
            Dict with has_regulatory_issues, headlines, source
        """
        result = {
            "has_regulatory_issues": False,
            "headlines": [],
            "source": "yfinance_news",
        }

        if not self._yf_available:
            return result

        try:
            ticker = self._yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return result

            regulatory_keywords = [
                "sec investigation", "sec inquiry", "sec probe",
                "enforcement", "fine", "penalty", "violation",
                "regulatory action", "doj", "department of justice",
                "class action", "lawsuit", "litigation",
            ]

            for article in news[:10]:  # Check recent 10 articles
                title = article.get("title", "").lower()
                summary = article.get("summary", "").lower()

                for keyword in regulatory_keywords:
                    if keyword in title or keyword in summary:
                        result["has_regulatory_issues"] = True
                        result["headlines"].append(article.get("title", ""))
                        break

        except Exception as e:
            print(f"[regulatory] Error checking news for {symbol}: {e}")

        return result

    def get_macro(self, region: str = "US") -> Optional[Dict]:
        """Fetch macro data for a region."""
        if self.mcp:
            if region == "US":
                return self.mcp.get_us_macro()
            elif region == "IN":
                nifty = self.mcp.get_nifty_valuation()
                fii = self.mcp.get_fii_dii_flows()
                return {"nifty": nifty, "fii_dii": fii}
        # Fallback: return minimal macro
        return {"region": region, "bias": "Selective", "source": "fallback"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
