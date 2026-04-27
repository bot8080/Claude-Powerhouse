"""Investment Brain CLI - Main entry point.

Usage:
    python main.py analyze TSM
    python main.py screen --pe-max 25 --roe-min 15 --sector Semis
    python main.py portfolio
    python main.py paper-buy TSM 10 175.50
    python main.py paper-sell TSM 10 185.00
    python main.py watchlist
    python main.py history
    python main.py export
    python main.py import backup.json
"""

import sys
import json
import argparse
from datetime import datetime
from typing import List, Optional

# Windows terminals default to cp1252 which can't render emoji — force UTF-8.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import DATA_DIR, MCP_SERVER_CMD, SCREENER_UNIVERSE
from data_fetcher import DataFetcher
from deal_breaker import check_deal_breakers
from scorer import score_stock
from portfolio_db import PortfolioDB
from paper_trading import PaperTradingEngine
from prompt_builder import PromptBuilder


def cmd_analyze(args):
    """Analyze a single stock."""
    ticker = args.ticker.upper()
    print(f"\n🔍 Analyzing {ticker}...")

    with DataFetcher() as fetcher:
        data = fetcher.get_stock_data(ticker, args.market or "US")
        if not data:
            print(f"❌ Failed to fetch data for {ticker}")
            return

        # Deal-breaker check
        db = check_deal_breakers(data)
        if db["blocked"]:
            print(f"\n⛔ BLOCKED: {ticker}")
            for r, e in zip(db["reasons"], db["evidence"]):
                print(f"   Reason: {r}")
                print(f"   Evidence: {e}")
            return

        # Score
        sector = data.get("profile", {}).get("identity", {}).get("sector", "")
        scores = score_stock(data, sector=sector)

        # Build prompt
        prompt = PromptBuilder.build_single_stock(data, scores)

        # Print results
        print(f"\n📊 Scores: Fund {scores['fundamentals']['score']}/35 | Tech {scores['technicals']['score']}/35 | SM {scores['smart_money']['score']}/30")
        print(f"   Total: {scores['total']}/100 | Verdict: {scores['verdict']}")
        print(f"   Account: {scores['account']} | Stop Loss: ${scores['stop_loss']}")
        print(f"\n📋 Copy this entire block into Claude:\n")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
        print(f"\n📋 Dashboard JSON (paste into artifact):\n")
        print(PromptBuilder.build_dashboard_json(data, scores))


def cmd_screen(args):
    """Run a stock screener."""
    print(f"\n🔍 Screening: PE < {args.pe_max}, ROE > {args.roe_min}%")
    if args.sector:
        print(f"   Sector: {args.sector}")

    # For screener, we need a universe. User provides tickers or we use SCREENER_UNIVERSE from config.
    tickers = args.tickers or SCREENER_UNIVERSE
    print(f"   Universe: {len(tickers)} stocks")

    with DataFetcher() as fetcher:
        results = []
        for t in tickers:
            data = fetcher.get_stock_data(t)
            if not data:
                continue
            db = check_deal_breakers(data)
            if db["blocked"]:
                continue
            sector = data.get("profile", {}).get("identity", {}).get("sector", "")
            if args.sector and sector != args.sector:
                continue
            scores = score_stock(data, sector=sector)

            # Filter by criteria
            raw = scores["fundamentals"]["raw"]
            pe = raw.get("pe")
            roe = raw.get("roe")
            if pe and pe > args.pe_max:
                continue
            if roe and roe < args.roe_min:
                continue

            results.append({"data": data, "scores": scores, "ticker": t})

        # Sort by total score
        results.sort(key=lambda x: x["scores"]["total"], reverse=True)

        print(f"\n✅ {len(results)} stocks passed screening")

        if results:
            criteria = f"PE < {args.pe_max}, ROE > {args.roe_min}%"
            if args.sector:
                criteria += f", Sector = {args.sector}"

            prompt = PromptBuilder.build_screener(results, criteria, len(tickers))

            print(f"\n📋 Copy this entire block into Claude:\n")
            print("=" * 60)
            print(prompt)
            print("=" * 60)

            # Save to DB
            db = PortfolioDB()
            db.add_screener_results([
                {
                    "t": r["ticker"],
                    "name": r["data"].get("profile", {}).get("identity", {}).get("name", ""),
                    "sector": r["data"].get("profile", {}).get("identity", {}).get("sector", ""),
                    "market": r["data"].get("market", "US"),
                    "price": r["data"].get("profile", {}).get("price", {}).get("current", 0),
                    "fund": r["scores"]["fundamentals"]["score"],
                    "tech": r["scores"]["technicals"]["score"],
                    "sm": r["scores"]["smart_money"]["score"],
                    "verdict": r["scores"]["verdict"],
                    "screen_meta": {"criteria": criteria, "rank": i + 1, "universe_size": len(tickers)},
                }
                for i, r in enumerate(results)
            ], criteria)
            print(f"\n💾 Saved {len(results)} results to database")


def cmd_portfolio(args):
    """Review portfolio."""
    db = PortfolioDB()
    holdings = db.get_portfolio()

    if not holdings:
        print("\n📭 Portfolio is empty. Add stocks first.")
        return

    print(f"\n📊 Portfolio Review ({len(holdings)} holdings)")
    total_value = sum(h.get("price", 0) * h.get("shares", 0) for h in holdings)
    total_cost = sum(h.get("cost", h.get("price", 0)) * h.get("shares", 0) for h in holdings)
    pnl = total_value - total_cost
    pnl_pct = (pnl / total_cost * 100) if total_cost else 0

    print(f"   Value: ${total_value:,.2f} | Cost: ${total_cost:,.2f} | P&L: {pnl:+.2f} ({pnl_pct:+.1f}%)")

    # Sector allocation
    sectors = {}
    for h in holdings:
        val = h.get("price", 0) * h.get("shares", 0)
        sectors[h.get("sector", "Unknown")] = sectors.get(h.get("sector", "Unknown"), 0) + val

    print(f"\n📊 Sector Allocation:")
    for s, v in sorted(sectors.items(), key=lambda x: -x[1]):
        pct = (v / total_value * 100) if total_value else 0
        flag = "🔴" if pct > 30 else "🟡" if pct > 20 else "🟢"
        print(f"   {flag} {s}: {pct:.1f}% (${v:,.2f})")

    # Flags
    print(f"\n🚨 Flags:")
    for h in holdings:
        flags = h.get("flags", [])
        if isinstance(flags, str):
            flags = json.loads(flags) if flags else []
        if flags:
            print(f"   {h['ticker']}: {', '.join(flags)}")

    # Build prompt
    sector_alloc = [{"sector": k, "pct": (v / total_value * 100) if total_value else 0} for k, v in sectors.items()]
    flags = []
    actions = []
    for h in holdings:
        val = h.get("price", 0) * h.get("shares", 0)
        pct = (val / total_value * 100) if total_value else 0
        if pct > 10:
            actions.append({"priority": 1, "t": h["ticker"], "action": "TRIM", "reason": f"Concentration: {pct:.1f}%"})
        if isinstance(h.get("flags"), list) and "deal_breaker" in h["flags"]:
            actions.append({"priority": 1, "t": h["ticker"], "action": "SELL", "reason": "Deal-breaker"})

    prompt = PromptBuilder.build_portfolio_review(holdings, sector_alloc, flags, actions)
    print(f"\n📋 Copy this into Claude for formatted output:\n")
    print("=" * 60)
    print(prompt)
    print("=" * 60)


def cmd_paper_buy(args):
    """Execute paper buy."""
    engine = PaperTradingEngine(PortfolioDB())
    result = engine.buy(
        ticker=args.ticker,
        shares=args.shares,
        entry=args.price,
        sector=args.sector or "",
        account=args.account or "TFSA",
        stop_loss=args.stop_loss,
        target=args.target,
    )

    if result["success"]:
        print(f"\n✅ Paper BUY executed: {result['ticker']}")
        print(f"   Shares: {result['shares']} @ ${result['entry']}")
        print(f"   Cost: ${result['cost']:,.2f}")
        print(f"   Stop Loss: ${result['stop_loss']}")
        if result["warnings"]:
            print(f"   ⚠️ Warnings: {', '.join(result['warnings'])}")

        # Build prompt
        impact = {
            "cash_before": engine.get_cash() + result["cost"],
            "cash_after": engine.get_cash(),
            "position_pct": (result["shares"] * result["entry"] / engine.get_total_value() * 100) if engine.get_total_value() else 0,
        }
        prompt = PromptBuilder.build_paper_trade_ticket(result, impact)
        print(f"\n📋 Copy this into Claude for formatted ticket:\n")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
    else:
        print(f"\n❌ Buy failed:")
        for e in result["errors"]:
            print(f"   • {e}")


def cmd_paper_sell(args):
    """Execute paper sell."""
    engine = PaperTradingEngine(PortfolioDB())
    result = engine.sell(args.ticker, args.shares, args.price, args.reason or "Manual close")

    if result["success"]:
        print(f"\n✅ Paper SELL executed: {result['ticker']}")
        print(f"   Shares: {result['shares']} @ ${result['exit']}")
        print(f"   P&L: {result['pnl_pct']:+.2f}% (${result['pnl_dollar']:+.2f})")
    else:
        print(f"\n❌ Sell failed:")
        for e in result["errors"]:
            print(f"   • {e}")


def cmd_watchlist(args):
    """Show watchlist."""
    db = PortfolioDB()
    items = db.get_watchlist()
    if not items:
        print("\n📭 Watchlist is empty.")
        return
    print(f"\n👀 Watchlist ({len(items)} items):")
    for item in items:
        total = (item.get("fund_score", 0) or 0) + (item.get("tech_score", 0) or 0) + (item.get("sm_score", 0) or 0)
        print(f"   {item['ticker']}: {total}/100 | {item.get('verdict', 'WATCH')} | ${item.get('price', 0)}")


def cmd_history(args):
    """Show decision history."""
    db = PortfolioDB()
    items = db.get_history()
    if not items:
        print("\n📭 No history yet.")
        return
    print(f"\n📜 Decision History ({len(items)} entries):")
    for h in items[:20]:
        print(f"   {h['date']} | {h['ticker']} | {h['action']} | {h['verdict']} | {h.get('reason', '')[:40]}")


def cmd_export(args):
    """Export all data to JSON."""
    db = PortfolioDB()
    data = db.get_all_data()
    path = args.file or f"investment_backup_{datetime.now().strftime('%Y%m%d')}.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n💾 Exported to {path}")


def cmd_import(args):
    """Import data from JSON."""
    with open(args.file, 'r') as f:
        data = json.load(f)
    db = PortfolioDB()
    db.import_all_data(data)
    print(f"\n📥 Imported from {args.file}")


def main():
    parser = argparse.ArgumentParser(description="Investment Brain CLI")
    subparsers = parser.add_subparsers(dest="command")

    # analyze
    p = subparsers.add_parser("analyze", help="Analyze a stock")
    p.add_argument("ticker", help="Ticker symbol")
    p.add_argument("--market", default="US", help="Market (US/CA/IN)")
    p.set_defaults(func=cmd_analyze)

    # screen
    p = subparsers.add_parser("screen", help="Run stock screener")
    p.add_argument("--pe-max", type=float, default=25, help="Max PE ratio")
    p.add_argument("--roe-min", type=float, default=15, help="Min ROE %")
    p.add_argument("--sector", help="Filter by sector")
    p.add_argument("tickers", nargs="*", help="Ticker universe (default: top 10 tech)")
    p.set_defaults(func=cmd_screen)

    # portfolio
    p = subparsers.add_parser("portfolio", help="Review portfolio")
    p.set_defaults(func=cmd_portfolio)

    # paper-buy
    p = subparsers.add_parser("paper-buy", help="Paper trade buy")
    p.add_argument("ticker", help="Ticker")
    p.add_argument("shares", type=float, help="Number of shares")
    p.add_argument("price", type=float, help="Entry price")
    p.add_argument("--sector", help="Sector")
    p.add_argument("--account", default="TFSA", help="Account")
    p.add_argument("--stop-loss", type=float, help="Stop loss price")
    p.add_argument("--target", type=float, help="Target price")
    p.set_defaults(func=cmd_paper_buy)

    # paper-sell
    p = subparsers.add_parser("paper-sell", help="Paper trade sell")
    p.add_argument("ticker", help="Ticker")
    p.add_argument("shares", type=float, help="Number of shares")
    p.add_argument("price", type=float, help="Exit price")
    p.add_argument("--reason", default="Manual close", help="Reason")
    p.set_defaults(func=cmd_paper_sell)

    # watchlist
    p = subparsers.add_parser("watchlist", help="Show watchlist")
    p.set_defaults(func=cmd_watchlist)

    # history
    p = subparsers.add_parser("history", help="Show decision history")
    p.set_defaults(func=cmd_history)

    # export
    p = subparsers.add_parser("export", help="Export data")
    p.add_argument("--file", help="Output file path")
    p.set_defaults(func=cmd_export)

    # import
    p = subparsers.add_parser("import", help="Import data")
    p.add_argument("file", help="JSON file to import")
    p.set_defaults(func=cmd_import)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
