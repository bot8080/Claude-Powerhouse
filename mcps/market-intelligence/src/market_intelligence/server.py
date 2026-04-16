from fastmcp import FastMCP

from market_intelligence.resolver import resolve_tickers_impl
from market_intelligence.profile import get_full_profile_impl, get_batch_profiles_impl
from market_intelligence.technicals import get_technicals_impl
from market_intelligence.india import get_fii_dii_flows_impl, get_nifty_valuation_impl
from market_intelligence.scoring import get_scoring_data_impl
from market_intelligence.activity import get_institutional_activity_impl
from market_intelligence.macro import get_us_macro_impl

mcp = FastMCP("market_intelligence")


@mcp.tool
def resolve_tickers(queries: list[str]) -> dict:
    """Resolve company names or partial tickers to exact Yahoo Finance symbols. ALWAYS call this BEFORE any other tool when the user mentions stocks. Handles dynamic lookup, suffix detection (.NS for India NSE, .TO for Canada TSX, .BO for India BSE, .L for London), and ambiguity. Returns resolved symbols, ambiguous matches, and failures. Never adds context words like 'India', 'stock', or 'NSE' to queries."""
    return resolve_tickers_impl(queries)


@mcp.tool
def get_full_profile(symbol: str) -> dict:
    """Get comprehensive stock profile in one call: price, valuation (PE, PEG, P/B, EV/EBITDA), quality (ROE, margins, debt), growth (revenue, earnings), analyst targets, risk (beta, insider%), and dividends. Use clean symbols only (e.g. 'NVDA', 'BEL.NS', 'SHOP.TO'). Always call resolve_tickers first if symbol may be ambiguous."""
    return get_full_profile_impl(symbol)


@mcp.tool
def get_batch_profiles(symbols: list[str]) -> dict:
    """Get full profiles for multiple stocks in one MCP call using parallel fetching. Returns profiles array + errors array + counts. Use for portfolio analysis of multiple tickers (up to 20 recommended). Replaces 14+ individual get_full_profile calls."""
    return get_batch_profiles_impl(symbols)


@mcp.tool
def get_technicals(symbol: str, period: str = "1y") -> dict:
    """Compute technical indicators server-side: RSI(14), MACD, ADX(14), ATR(14), Bollinger Bands(20), MFI(14), OBV, SMA 50/200, Golden/Death Cross, trend strength, and overall signal. Period options: 1mo, 3mo, 6mo, 1y, 2y, 5y. Requires 50+ data points. Returns suggested stop loss (price - 2×ATR)."""
    return get_technicals_impl(symbol, period)


@mcp.tool
def get_fii_dii_flows(days: int = 20) -> dict:
    """Get FII (Foreign Institutional Investor) and DII (Domestic Institutional Investor) daily flow data from NSE India. Returns daily buy/sell/net breakdown, rolling totals, and sentiment signal (e.g. 'DII absorbing FII selling'). India market only. Data sourced from nsepython."""
    return get_fii_dii_flows_impl(days)


@mcp.tool
def get_nifty_valuation() -> dict:
    """Get Nifty 50 index P/E, P/B, dividend yield, year high/low, and valuation zone (Excellent <18, Good 18-22, Fair 22-25, Expensive 25-28, Bubble >28) with action guidance. Use as macro overlay before analyzing Indian stocks. Data sourced from nsetools with yfinance fallback."""
    return get_nifty_valuation_impl()


@mcp.tool
def get_scoring_data(symbol: str) -> dict:
    """Pre-compute a 4-pillar investment score (Valuation + Quality + Momentum + Risk, 25pts each, 100 total) with deal-breaker checks. Deal-breakers: current_ratio<0.5, debt_to_equity>500, or no revenue+earnings. Returns pillar scores with reasons, total score, verdict suggestion (BUY/HOLD/SELL), and raw profile + technicals data for Claude to refine the analysis."""
    return get_scoring_data_impl(symbol)


@mcp.tool
def get_institutional_activity(symbol: str) -> dict:
    """Get institutional activity for a stock: insider buy/sell transactions, top institutional holders (Vanguard, BlackRock etc.) with % held and change, mutual fund holders, analyst upgrades/downgrades with price targets, earnings calendar, and major holders summary. Works for US and Canadian stocks. For Indian stocks, insider/institutional data is not available via Yahoo Finance — use get_fii_dii_flows instead for India institutional sentiment."""
    return get_institutional_activity_impl(symbol)

@mcp.tool
def get_us_macro() -> dict:
    """Get US macro environment: VIX fear gauge (calm/elevated/crisis), 10Y-3M yield curve spread (normal/flattening/inverted), DXY US Dollar trend (headwind/tailwind), and S&P 500 200DMA trend. Returns a combined macro_summary signal. Call this before analysing any US/Canada stock for macro context. VIX > 30 = avoid new positions. Inverted yield curve = recession risk. All data via yfinance, no extra API keys needed."""
    return get_us_macro_impl()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
