"""Prompt Builder - Creates minimal, copy-paste-ready prompts for Claude.

Takes scored data and outputs a tiny prompt + structured JSON.
Claude only needs to format - no research, no scoring, no tool calls.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class PromptBuilder:
    """Builds minimal prompts for Claude formatting."""

    SYSTEM_HINT = """Format this stock data into a Summary Card per my rules.
Rules: Fundamentals 35, Technicals 35, Smart Money 30. Traffic lights.
One verdict. One action line with price and stop loss.
3 news bullets. 3 top risks. Decision log last.
No prose paragraphs. Tables only."""

    @classmethod
    def build_single_stock(cls, data: Dict, scores: Dict, news: List[str] = None,
                           bear_case: str = "", macro: Dict = None) -> str:
        """Build prompt for single stock analysis.

        Returns a string: first line is the tiny prompt, rest is JSON.
        User copies entire string and pastes into Claude.
        """
        profile = data.get("profile", {})
        identity = profile.get("identity", {})
        price_data = profile.get("price", {})

        payload = {
            "mode": "format_single",
            "ticker": data.get("symbol", ""),
            "name": identity.get("name", ""),
            "sector": identity.get("sector", ""),
            "market": data.get("market", "US"),
            "account": scores.get("account", "TFSA"),
            "price": price_data.get("current", 0),
            "fifty_two_week_low": price_data.get("fifty_two_week_low"),
            "fifty_two_week_high": price_data.get("fifty_two_week_high"),
            "market_cap": identity.get("market_cap"),

            "fund_score": scores["fundamentals"]["score"],
            "fund_max": 35,
            "fund_breakdown": scores["fundamentals"]["breakdown"],
            "fund_raw": scores["fundamentals"]["raw"],

            "tech_score": scores["technicals"]["score"],
            "tech_max": 35,
            "tech_breakdown": scores["technicals"]["breakdown"],
            "tech_raw": scores["technicals"]["raw"],

            "sm_score": scores["smart_money"]["score"],
            "sm_max": 30,
            "sm_breakdown": scores["smart_money"]["breakdown"],
            "sm_raw": scores["smart_money"].get("raw", {}),
            "sm_note": scores["smart_money"].get("note", ""),

            "total_score": scores["total"],
            "verdict": scores["verdict"],
            "stop_loss": scores["stop_loss"],
            "price_zones": scores["price_zones"],

            "news": news or ["⚠️ No material news in last 30 days."],
            "bear_case": bear_case or "No explicit bear case identified.",
            "macro": macro or {},
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Add deal-breaker info if present
        if data.get("deal_breaker"):
            payload["blocked"] = True
            payload["deal_breaker"] = data["deal_breaker"]

        return f"{cls.SYSTEM_HINT}\n\n```json\n{json.dumps(payload, indent=2, default=str)}\n```"

    @classmethod
    def build_batch(cls, items: List[Dict]) -> str:
        """Build prompt for batch comparison (3+ stocks)."""
        payload = {
            "mode": "format_batch",
            "stocks": [
                {
                    "ticker": item["data"].get("symbol", ""),
                    "name": item["data"].get("profile", {}).get("identity", {}).get("name", ""),
                    "fund": item["scores"]["fundamentals"]["score"],
                    "tech": item["scores"]["technicals"]["score"],
                    "sm": item["scores"]["smart_money"]["score"],
                    "total": item["scores"]["total"],
                    "verdict": item["scores"]["verdict"],
                    "price": item["data"].get("profile", {}).get("price", {}).get("current", 0),
                    "sector": item["data"].get("profile", {}).get("identity", {}).get("sector", ""),
                }
                for item in items
            ],
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        return f"Format these stocks as a comparison table + brief cards for top 3. Per my output_format.md rules.\n\n```json\n{json.dumps(payload, indent=2, default=str)}\n```"

    @classmethod
    def build_portfolio_review(cls, holdings: List[Dict], sector_alloc: List[Dict],
                               flags: List[Dict], actions: List[Dict],
                               paper_summary: Optional[Dict] = None) -> str:
        """Build prompt for portfolio review."""
        payload = {
            "mode": "format_portfolio",
            "holdings": holdings,
            "sector_allocation": sector_alloc,
            "flags": flags,
            "actions": actions,
            "paper_summary": paper_summary,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        return f"Format this portfolio review per my rules. Holdings scoreboard + sector allocation + action items. Per output_format.md.\n\n```json\n{json.dumps(payload, indent=2, default=str)}\n```"

    @classmethod
    def build_screener(cls, results: List[Dict], criteria: str, universe_size: int) -> str:
        """Build prompt for screener results."""
        payload = {
            "mode": "format_screener",
            "criteria": criteria,
            "universe_size": universe_size,
            "results": [
                {
                    "rank": i + 1,
                    "ticker": r["data"].get("symbol", ""),
                    "name": r["data"].get("profile", {}).get("identity", {}).get("name", ""),
                    "sector": r["data"].get("profile", {}).get("identity", {}).get("sector", ""),
                    "price": r["data"].get("profile", {}).get("price", {}).get("current", 0),
                    "fund": r["scores"]["fundamentals"]["score"],
                    "tech": r["scores"]["technicals"]["score"],
                    "sm": r["scores"]["smart_money"]["score"],
                    "total": r["scores"]["total"],
                    "verdict": r["scores"]["verdict"],
                }
                for i, r in enumerate(results[:10])
            ],
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        return f"Format these screener results per my rules. Comparison table + brief cards for top 3. Per output_format.md.\n\n```json\n{json.dumps(payload, indent=2, default=str)}\n```"

    @classmethod
    def build_paper_trade_ticket(cls, trade_result: Dict, portfolio_impact: Dict) -> str:
        """Build prompt for paper trade ticket."""
        payload = {
            "mode": "format_paper_trade",
            "trade": trade_result,
            "impact": portfolio_impact,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        return f"Format this paper trade as a Trade Ticket + portfolio impact table. Per output_format.md rules.\n\n```json\n{json.dumps(payload, indent=2, default=str)}\n```"

    @classmethod
    def build_dashboard_json(cls, data: Dict, scores: Dict) -> str:
        """Build the dashboard-ready JSON block (what user pastes into artifact)."""
        payload = {
            "t": data.get("symbol", ""),
            "name": data.get("profile", {}).get("identity", {}).get("name", ""),
            "sector": data.get("profile", {}).get("identity", {}).get("sector", ""),
            "market": data.get("market", "US"),
            "account": scores.get("account", "TFSA"),
            "price": data.get("profile", {}).get("price", {}).get("current", 0),
            "fund": scores["fundamentals"]["score"],
            "tech": scores["technicals"]["score"],
            "sm": scores["smart_money"]["score"],
            "verdict": scores["verdict"],
            "flags": cls._derive_flags(data, scores),
            "notes": f"{scores['verdict']}. Stop ${scores['stop_loss']}.",
            "stopLoss": scores["stop_loss"],
            "added": datetime.now().strftime("%Y-%m-%d"),
        }
        return json.dumps(payload, indent=2, default=str)

    @classmethod
    def _derive_flags(cls, data: Dict, scores: Dict) -> List[str]:
        """Auto-derive flags from scores and data."""
        flags = []
        profile = data.get("profile", {})

        if scores["verdict"] == "BLOCKED":
            flags.append("deal_breaker")
        if scores["total"] >= 80:
            pass  # strong score, no flag needed
        elif scores["fundamentals"]["score"] < 17:
            flags.append("weak_fundamentals")
        if scores["price_zones"].get("current", 0) > scores["price_zones"].get("expensive", 999999):
            flags.append("above_fair_value")

        # Check for specific conditions
        de = scores["fundamentals"]["raw"].get("de")
        if de and de > 200:
            flags.append("high_leverage")

        fcf = scores["fundamentals"]["raw"].get("fcf")
        if fcf is not None and fcf < 0:
            flags.append("neg_fcf")

        return flags
