"""Portfolio Database - SQLite-backed portfolio, watchlist, and history.

Lightweight, no ORM. Pure sqlite3.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import DATA_DIR


class PortfolioDB:
    """SQLite database for portfolio, watchlist, screener results, and history."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DATA_DIR / "portfolio.db")
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if not exist."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    ticker TEXT PRIMARY KEY,
                    name TEXT,
                    sector TEXT,
                    market TEXT,
                    account TEXT,
                    price REAL,
                    cost REAL,
                    shares REAL,
                    fund_score INTEGER,
                    tech_score INTEGER,
                    sm_score INTEGER,
                    verdict TEXT,
                    flags TEXT,
                    notes TEXT,
                    stop_loss REAL,
                    added TEXT,
                    updated TEXT
                );

                CREATE TABLE IF NOT EXISTS watchlist (
                    ticker TEXT PRIMARY KEY,
                    name TEXT,
                    sector TEXT,
                    market TEXT,
                    account TEXT,
                    price REAL,
                    fund_score INTEGER,
                    tech_score INTEGER,
                    sm_score INTEGER,
                    verdict TEXT,
                    flags TEXT,
                    notes TEXT,
                    stop_loss REAL,
                    added TEXT,
                    updated TEXT
                );

                CREATE TABLE IF NOT EXISTS screener_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    name TEXT,
                    sector TEXT,
                    market TEXT,
                    account TEXT,
                    price REAL,
                    fund_score INTEGER,
                    tech_score INTEGER,
                    sm_score INTEGER,
                    verdict TEXT,
                    flags TEXT,
                    notes TEXT,
                    stop_loss REAL,
                    screen_criteria TEXT,
                    screen_rank INTEGER,
                    universe_size INTEGER,
                    added TEXT
                );

                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    ticker TEXT,
                    action TEXT,
                    verdict TEXT,
                    score INTEGER,
                    reason TEXT,
                    mode TEXT
                );

                CREATE TABLE IF NOT EXISTS macro (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    us_data TEXT,
                    india_data TEXT,
                    updated TEXT
                );
            """)
            conn.commit()

    # ─── Portfolio ───
    def add_to_portfolio(self, stock: Dict):
        """Add or update a portfolio position."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO portfolio
                (ticker, name, sector, market, account, price, cost, shares,
                 fund_score, tech_score, sm_score, verdict, flags, notes,
                 stop_loss, added, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock.get("t", stock.get("ticker")),
                stock.get("name", ""),
                stock.get("sector", ""),
                stock.get("market", "US"),
                stock.get("account", "TFSA"),
                stock.get("price", 0),
                stock.get("cost", stock.get("price", 0)),
                stock.get("shares", 0),
                stock.get("fund", 0),
                stock.get("tech", 0),
                stock.get("sm", 0),
                stock.get("verdict", "HOLD"),
                json.dumps(stock.get("flags", [])),
                stock.get("notes", ""),
                stock.get("stopLoss"),
                stock.get("added", datetime.now().strftime("%Y-%m-%d")),
                datetime.now().strftime("%Y-%m-%d"),
            ))
            conn.commit()

    def get_portfolio(self) -> List[Dict]:
        """Get all portfolio positions."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM portfolio ORDER BY ticker").fetchall()
            return [self._row_to_dict(r) for r in rows]

    def remove_from_portfolio(self, ticker: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker,))
            conn.commit()

    # ─── Watchlist ───
    def add_to_watchlist(self, stock: Dict):
        """Add or update watchlist entry."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO watchlist
                (ticker, name, sector, market, account, price,
                 fund_score, tech_score, sm_score, verdict, flags, notes,
                 stop_loss, added, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock.get("t", stock.get("ticker")),
                stock.get("name", ""),
                stock.get("sector", ""),
                stock.get("market", "US"),
                stock.get("account", "TFSA"),
                stock.get("price", 0),
                stock.get("fund", 0),
                stock.get("tech", 0),
                stock.get("sm", 0),
                stock.get("verdict", "WATCH"),
                json.dumps(stock.get("flags", [])),
                stock.get("notes", ""),
                stock.get("stopLoss"),
                stock.get("added", datetime.now().strftime("%Y-%m-%d")),
                datetime.now().strftime("%Y-%m-%d"),
            ))
            conn.commit()

    def get_watchlist(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM watchlist ORDER BY ticker").fetchall()
            return [self._row_to_dict(r) for r in rows]

    def remove_from_watchlist(self, ticker: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
            conn.commit()

    # ─── Screener ───
    def add_screener_results(self, results: List[Dict], criteria: str = ""):
        """Add screener results. Clears old results first."""
        with self._connect() as conn:
            conn.execute("DELETE FROM screener_results")
            for i, stock in enumerate(results):
                conn.execute("""
                    INSERT INTO screener_results
                    (ticker, name, sector, market, account, price,
                     fund_score, tech_score, sm_score, verdict, flags, notes,
                     stop_loss, screen_criteria, screen_rank, universe_size, added)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock.get("t", stock.get("ticker")),
                    stock.get("name", ""),
                    stock.get("sector", ""),
                    stock.get("market", "US"),
                    stock.get("account", "TFSA"),
                    stock.get("price", 0),
                    stock.get("fund", 0),
                    stock.get("tech", 0),
                    stock.get("sm", 0),
                    stock.get("verdict", "WATCH"),
                    json.dumps(stock.get("flags", [])),
                    stock.get("notes", ""),
                    stock.get("stopLoss"),
                    criteria,
                    stock.get("screen_meta", {}).get("rank", i + 1),
                    stock.get("screen_meta", {}).get("universe_size", len(results)),
                    datetime.now().strftime("%Y-%m-%d"),
                ))
            conn.commit()

    def get_screener_results(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM screener_results ORDER BY screen_rank").fetchall()
            return [self._row_to_dict(r) for r in rows]

    # ─── History ───
    def log_decision(self, entry: Dict):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO history (date, ticker, action, verdict, score, reason, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get("date", datetime.now().strftime("%Y-%m-%d")),
                entry.get("t", entry.get("ticker")),
                entry.get("action", ""),
                entry.get("verdict", ""),
                entry.get("score"),
                entry.get("reason", ""),
                entry.get("mode", ""),
            ))
            conn.commit()

    def get_history(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM history ORDER BY date DESC, id DESC").fetchall()
            return [dict(r) for r in rows]

    # ─── Macro ───
    def save_macro(self, macro: Dict):
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO macro (id, us_data, india_data, updated)
                VALUES (1, ?, ?, ?)
            """, (
                json.dumps(macro.get("us", {})),
                json.dumps(macro.get("india", {})),
                macro.get("updated", datetime.now().strftime("%Y-%m-%d")),
            ))
            conn.commit()

    def get_macro(self) -> Dict:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM macro WHERE id = 1").fetchone()
            if row:
                return {
                    "us": json.loads(row["us_data"] or "{}"),
                    "india": json.loads(row["india_data"] or "{}"),
                    "updated": row["updated"],
                }
            return {}

    # ─── Helpers ───
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        d = dict(row)
        if "flags" in d and d["flags"]:
            try:
                d["flags"] = json.loads(d["flags"])
            except:
                d["flags"] = []
        return d

    def get_all_data(self) -> Dict:
        """Export all data for backup/transfer."""
        return {
            "portfolio": self.get_portfolio(),
            "watchlist": self.get_watchlist(),
            "screenerResults": self.get_screener_results(),
            "history": self.get_history(),
            "macro": self.get_macro(),
        }

    def import_all_data(self, data: Dict):
        """Import all data from backup."""
        for stock in data.get("portfolio", []):
            self.add_to_portfolio(stock)
        for stock in data.get("watchlist", []):
            self.add_to_watchlist(stock)
        for entry in data.get("history", []):
            self.log_decision(entry)
        if data.get("macro"):
            self.save_macro(data["macro"])
