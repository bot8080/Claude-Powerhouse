"""Paper Trading Engine - Virtual portfolio with rules enforcement.

Stored in SQLite alongside portfolio data.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

from config import (
    PAPER_STARTING_CASH, PAPER_MAX_POSITION_PCT, PAPER_MAX_SECTOR_PCT,
    PAPER_MIN_CASH_PCT, PAPER_DEFAULT_STOP_LOSS_PCT, PAPER_MAX_POSITIONS
)
from portfolio_db import PortfolioDB


class PaperTradingEngine:
    """Virtual trading with rule enforcement."""

    def __init__(self, db: PortfolioDB):
        self.db = db
        self._init_tables()
        self._ensure_cash()

    def _connect(self):
        return self.db._connect()

    def _init_tables(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS paper_cash (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    balance REAL DEFAULT 50000.0
                );
                CREATE TABLE IF NOT EXISTS paper_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT UNIQUE,
                    shares REAL,
                    entry REAL,
                    price REAL,
                    stop_loss REAL,
                    target REAL,
                    sector TEXT,
                    account TEXT,
                    date TEXT,
                    status TEXT DEFAULT 'OPEN'
                );
                CREATE TABLE IF NOT EXISTS paper_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    ticker TEXT,
                    action TEXT,
                    shares REAL,
                    entry REAL,
                    exit REAL,
                    realized_pnl TEXT,
                    realized_pnl_dollar REAL,
                    status TEXT,
                    reason TEXT
                );
            """)
            conn.commit()

    def _ensure_cash(self):
        with self._connect() as conn:
            row = conn.execute("SELECT balance FROM paper_cash WHERE id = 1").fetchone()
            if not row:
                conn.execute("INSERT INTO paper_cash (id, balance) VALUES (1, ?)", (PAPER_STARTING_CASH,))
                conn.commit()

    def get_cash(self) -> float:
        with self._connect() as conn:
            row = conn.execute("SELECT balance FROM paper_cash WHERE id = 1").fetchone()
            return row["balance"] if row else PAPER_STARTING_CASH

    def get_positions(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM paper_positions WHERE status = 'OPEN' ORDER BY ticker").fetchall()
            return [dict(r) for r in rows]

    def get_history(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM paper_history ORDER BY date DESC, id DESC").fetchall()
            return [dict(r) for r in rows]

    def get_portfolio_value(self) -> float:
        positions = self.get_positions()
        return sum(p["shares"] * (p["price"] or p["entry"]) for p in positions)

    def get_total_value(self) -> float:
        return self.get_cash() + self.get_portfolio_value()

    def get_sector_allocation(self) -> Dict[str, float]:
        positions = self.get_positions()
        total = self.get_portfolio_value()
        if total == 0:
            return {}
        sectors = {}
        for p in positions:
            val = p["shares"] * (p["price"] or p["entry"])
            sectors[p.get("sector", "Unknown")] = sectors.get(p.get("sector", "Unknown"), 0) + val
        return {k: (v / total) * 100 for k, v in sectors.items()}

    def validate_buy(self, ticker: str, shares: float, entry: float, sector: str = "") -> Dict:
        """Validate a paper buy against rules. Returns {ok: bool, errors: [str], warnings: [str]}."""
        cash = self.get_cash()
        total_value = self.get_total_value()
        cost = shares * entry
        positions = self.get_positions()
        sector_alloc = self.get_sector_allocation()

        errors = []
        warnings = []

        # Cash check
        if cost > cash:
            errors.append(f"Insufficient cash: need ${cost:,.2f}, have ${cash:,.2f}")

        # Position size
        position_value = shares * entry
        position_pct = (position_value / total_value) * 100 if total_value > 0 else 0
        if position_pct > PAPER_MAX_POSITION_PCT:
            errors.append(f"Position size {position_pct:.1f}% > max {PAPER_MAX_POSITION_PCT}%")

        # Sector concentration
        current_sector_pct = sector_alloc.get(sector, 0)
        new_sector_pct = ((current_sector_pct / 100) * self.get_portfolio_value() + position_value) / total_value * 100 if total_value > 0 else 0
        if new_sector_pct > PAPER_MAX_SECTOR_PCT:
            errors.append(f"Sector {sector} would be {new_sector_pct:.1f}% > max {PAPER_MAX_SECTOR_PCT}%")

        # Max positions
        if len(positions) >= PAPER_MAX_POSITIONS:
            errors.append(f"Max {PAPER_MAX_POSITIONS} positions reached")

        # Cash buffer
        remaining_cash = cash - cost
        remaining_pct = (remaining_cash / total_value) * 100 if total_value > 0 else 0
        if remaining_pct < PAPER_MIN_CASH_PCT:
            warnings.append(f"Cash buffer will be {remaining_pct:.1f}% < min {PAPER_MIN_CASH_PCT}%")

        return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings}

    def buy(self, ticker: str, shares: float, entry: float, sector: str = "",
            account: str = "TFSA", stop_loss: Optional[float] = None,
            target: Optional[float] = None) -> Dict:
        """Execute a paper buy."""
        validation = self.validate_buy(ticker, shares, entry, sector)
        if not validation["ok"]:
            return {"success": False, "errors": validation["errors"]}

        cost = shares * entry
        sl = stop_loss or round(entry * (1 - PAPER_DEFAULT_STOP_LOSS_PCT / 100), 2)

        with self._connect() as conn:
            # Deduct cash
            conn.execute("UPDATE paper_cash SET balance = balance - ? WHERE id = 1", (cost,))
            # Add position
            conn.execute("""
                INSERT OR REPLACE INTO paper_positions
                (ticker, shares, entry, price, stop_loss, target, sector, account, date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
            """, (ticker.upper(), shares, entry, entry, sl, target, sector, account,
                  datetime.now().strftime("%Y-%m-%d")))
            conn.commit()

        return {
            "success": True,
            "ticker": ticker.upper(),
            "shares": shares,
            "entry": entry,
            "cost": cost,
            "stop_loss": sl,
            "warnings": validation["warnings"],
        }

    def sell(self, ticker: str, shares: float, exit_price: float, reason: str = "Manual close") -> Dict:
        """Execute a paper sell (full or partial)."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM paper_positions WHERE ticker = ? AND status = 'OPEN'", (ticker.upper(),)).fetchone()
            if not row:
                return {"success": False, "errors": [f"No open position for {ticker}"]}

            pos = dict(row)
            sell_shares = min(shares, pos["shares"])
            proceeds = sell_shares * exit_price
            cost_basis = sell_shares * pos["entry"]
            pnl_dollar = proceeds - cost_basis
            pnl_pct = ((exit_price - pos["entry"]) / pos["entry"]) * 100 if pos["entry"] else 0

            # Add cash
            conn.execute("UPDATE paper_cash SET balance = balance + ? WHERE id = 1", (proceeds,))

            # Update or remove position
            remaining = pos["shares"] - sell_shares
            if remaining > 0:
                conn.execute("UPDATE paper_positions SET shares = ? WHERE id = ?", (remaining, pos["id"]))
            else:
                conn.execute("UPDATE paper_positions SET status = 'CLOSED' WHERE id = ?", (pos["id"],))

            # Log history
            conn.execute("""
                INSERT INTO paper_history (date, ticker, action, shares, entry, exit, realized_pnl, realized_pnl_dollar, status, reason)
                VALUES (?, ?, 'SELL', ?, ?, ?, ?, ?, 'CLOSED', ?)
            """, (datetime.now().strftime("%Y-%m-%d"), ticker.upper(), sell_shares,
                  pos["entry"], exit_price, f"{pnl_pct:+.2f}%", pnl_dollar, reason))
            conn.commit()

        return {
            "success": True,
            "ticker": ticker.upper(),
            "shares": sell_shares,
            "exit": exit_price,
            "pnl_pct": pnl_pct,
            "pnl_dollar": pnl_dollar,
        }

    def update_price(self, ticker: str, price: float):
        """Update current price for an open position."""
        with self._connect() as conn:
            conn.execute("UPDATE paper_positions SET price = ? WHERE ticker = ? AND status = 'OPEN'",
                        (price, ticker.upper()))
            conn.commit()

    def check_stop_losses(self) -> List[Dict]:
        """Check for triggered stop losses."""
        triggered = []
        for p in self.get_positions():
            if p["price"] and p["stop_loss"] and p["price"] <= p["stop_loss"]:
                triggered.append({
                    "ticker": p["ticker"],
                    "price": p["price"],
                    "stop_loss": p["stop_loss"],
                    "action": "STOP_LOSS_TRIGGERED",
                })
        return triggered

    def get_summary(self) -> Dict:
        """Get paper portfolio summary."""
        positions = self.get_positions()
        history = self.get_history()
        cash = self.get_cash()
        open_value = self.get_portfolio_value()
        total = cash + open_value

        realized_pnl = sum(h.get("realized_pnl_dollar", 0) or 0 for h in history)
        unrealized_pnl = sum(
            p["shares"] * ((p["price"] or p["entry"]) - p["entry"]) for p in positions
        )

        return {
            "cash": cash,
            "open_value": open_value,
            "total_value": total,
            "open_positions": len(positions),
            "closed_trades": len(history),
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": realized_pnl + unrealized_pnl,
            "sector_allocation": self.get_sector_allocation(),
        }
