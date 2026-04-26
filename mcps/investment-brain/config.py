"""Investment Brain Configuration

Edit these settings for your setup.
"""

import os
from pathlib import Path

# ─── Paths ───
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ─── MCP Server ───
# Path to your market-intelligence MCP server
# Example: "uv run --directory C:/.../market-intelligence python -m market_intelligence"
# Leave empty to use yfinance fallback only
MCP_SERVER_CMD = "uv run --directory C:/Users/abhik/OneDrive/Documents/Projects/Claude-Powerhouse/mcps/market-intelligence python -m market_intelligence"

# ─── Markets ───
DEFAULT_MARKET = "US"  # US, CA, IN

# ─── Accounts ───
ACCOUNT_MAP = {
    "US": "TFSA",
    "CA": "TFSA",
    "IN": "Direct MF",
}

# ─── Scoring Weights ───
FUNDAMENTALS_MAX = 35
TECHNICALS_MAX = 35
SMART_MONEY_MAX = 30
TOTAL_MAX = 100

# ─── Deal-Breaker Thresholds ───
DEAL_BREAKERS = {
    "current_ratio_min": 0.5,
    "debt_equity_max": 500,
    "fcf_negative_years": 2,
    "insider_sell_pct_90d": 20,
    "promoter_pledge_max": 50,  # India
    "qoef_ratio_min": 0.7,
    "altman_z_min": 1.81,
}

# ─── Sector Overrides ───
SECTOR_OVERRIDES = {
    "Banks": {"skip_altman": True, "use_cet1": True, "pe_range": (8, 18)},
    "Insurance": {"skip_altman": True, "use_combined_ratio": True, "pe_range": (10, 20)},
    "REIT": {"skip_pe": True, "use_p_ffo": True, "dividend_weight": 2.0},
    "Energy": {"pe_weight": 0.5, "ev_ebitda_weight": 1.5},
    "Commodities": {"pe_weight": 0.5, "ev_ebitda_weight": 1.5},
}

# ─── Paper Trading ───
PAPER_STARTING_CASH = 50000.0
PAPER_MAX_POSITION_PCT = 10.0
PAPER_MAX_SECTOR_PCT = 30.0
PAPER_MIN_CASH_PCT = 10.0
PAPER_DEFAULT_STOP_LOSS_PCT = 10.0
PAPER_MAX_POSITIONS = 25

# ─── Reference Scales ───
PE_SCALE = {"green": 20, "yellow": 35, "red": 999}
PEG_SCALE = {"green": 1.0, "yellow": 2.0, "red": 999}
EV_EBITDA_SCALE = {"green": 15, "yellow": 25, "red": 999}
ROE_SCALE = {"green": 15, "yellow": 8, "red": 0}
OP_MARGIN_SCALE = {"green": 20, "yellow": 10, "red": 0}
DE_SCALE = {"green": 50, "yellow": 200, "red": 500}
CURR_RATIO_SCALE = {"green": 1.5, "yellow": 1.0, "red": 0.5}
RSI_SCALE = {"oversold": 30, "neutral_low": 45, "neutral_high": 65, "overbought": 70}

# ─── Output ───
DATE_FORMAT = "%Y-%m-%d"
