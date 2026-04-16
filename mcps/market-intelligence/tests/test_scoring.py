"""Tests for scoring module — pillar scores + deal-breakers."""
import pytest
from unittest.mock import patch

from market_intelligence.scoring import (
    _safe,
    _score_valuation,
    _score_quality,
    _score_momentum,
    _score_risk,
    _verdict,
    get_scoring_data_impl,
)


# ── _safe ───────────────────────────────────────────────────────

class TestSafe:
    def test_value(self):
        assert _safe(42) == 42

    def test_none_with_default(self):
        assert _safe(None, 0) == 0

    def test_none_without_default(self):
        assert _safe(None) is None


# ── _score_valuation ────────────────────────────────────────────

class TestScoreValuation:
    def test_pe_very_low(self):
        profile = {"valuation": {"pe_trailing": 12, "peg_ratio": 0.8}}
        result = _score_valuation(profile)
        assert result["score"] == 23  # PE<15 + PEG<1 = 23
        assert result["max"] == 25

    def test_pe_low_with_good_peg(self):
        profile = {"valuation": {"pe_trailing": 18, "peg_ratio": 1.2}}
        result = _score_valuation(profile)
        assert result["score"] == 20  # PEG < 1.5 → base=20

    def test_pe_low_without_peg(self):
        profile = {"valuation": {"pe_trailing": 18}}
        result = _score_valuation(profile)
        assert result["score"] == 17  # no PEG → base=17

    def test_pe_fair(self):
        profile = {"valuation": {"pe_trailing": 23}}
        result = _score_valuation(profile)
        assert result["score"] == 15

    def test_pe_elevated(self):
        profile = {"valuation": {"pe_trailing": 30}}
        result = _score_valuation(profile)
        assert result["score"] == 10

    def test_pe_high(self):
        profile = {"valuation": {"pe_trailing": 45}}
        result = _score_valuation(profile)
        assert result["score"] == 5

    def test_pe_very_high(self):
        profile = {"valuation": {"pe_trailing": 100}}
        result = _score_valuation(profile)
        assert result["score"] == 2

    def test_pe_none(self):
        profile = {"valuation": {}}
        result = _score_valuation(profile)
        assert result["score"] == 10  # neutral

    def test_peg_bonus(self):
        profile = {"valuation": {"pe_trailing": 23, "peg_ratio": 0.9}}
        result = _score_valuation(profile)
        assert result["score"] == 17  # 15 + 2 bonus


# ── _score_quality ──────────────────────────────────────────────

class TestScoreQuality:
    def test_excellent_quality(self):
        profile = {
            "quality": {"roe": 0.20, "debt_to_equity": 50, "profit_margin": 0.20},
            "risk": {"insider_pct": 0.12},
        }
        result = _score_quality(profile)
        assert result["score"] == 23  # 15 (ROE) + 5 (insider) + 3 (moat default)
        assert result["max"] == 25

    def test_weak_quality(self):
        profile = {
            "quality": {"roe": 0.05, "debt_to_equity": 250},
            "risk": {"insider_pct": 0.02},
        }
        result = _score_quality(profile)
        # ROE: 5 - 3 (D/E penalty) = 2, insider=1, moat=3
        assert result["score"] == 6

    def test_missing_data(self):
        profile = {"quality": {}, "risk": {}}
        result = _score_quality(profile)
        # ROE unavailable=6, insider unavailable=2, moat=3
        assert result["score"] == 11


# ── _score_momentum ─────────────────────────────────────────────

class TestScoreMomentum:
    def test_all_bullish(self):
        technicals = {
            "trend": {"above_200dma": True, "above_50dma": True},
            "momentum": {"rsi_14": 55, "macd_bullish": True},
            "strength": {"adx_14": 30},
        }
        result = _score_momentum(technicals)
        assert result["score"] == 25
        assert result["max"] == 25

    def test_all_bearish(self):
        technicals = {
            "trend": {"above_200dma": False, "above_50dma": False},
            "momentum": {"rsi_14": 80, "macd_bullish": False},
            "strength": {"adx_14": 15},
        }
        result = _score_momentum(technicals)
        assert result["score"] == 0

    def test_error_in_technicals(self):
        result = _score_momentum({"error": "no data"})
        assert result["score"] == 10  # neutral fallback


# ── _score_risk ─────────────────────────────────────────────────

class TestScoreRisk:
    def test_low_beta(self):
        result = _score_risk({"risk": {"beta": 1.0}})
        assert result["score"] == 25

    def test_slightly_elevated(self):
        result = _score_risk({"risk": {"beta": 1.3}})
        assert result["score"] == 20

    def test_elevated(self):
        result = _score_risk({"risk": {"beta": 1.7}})
        assert result["score"] == 15

    def test_high(self):
        result = _score_risk({"risk": {"beta": 2.2}})
        assert result["score"] == 10

    def test_very_high(self):
        result = _score_risk({"risk": {"beta": 3.0}})
        assert result["score"] == 5

    def test_none(self):
        result = _score_risk({"risk": {}})
        assert result["score"] == 15  # neutral


# ── _verdict ────────────────────────────────────────────────────

class TestVerdict:
    def test_buy(self):
        assert _verdict(85) == "BUY"

    def test_buy_hold(self):
        assert _verdict(70) == "BUY/HOLD"

    def test_hold(self):
        assert _verdict(55) == "HOLD"

    def test_hold_sell(self):
        assert _verdict(40) == "HOLD/SELL"

    def test_sell(self):
        assert _verdict(20) == "SELL"

    def test_boundaries(self):
        assert _verdict(80) == "BUY"
        assert _verdict(65) == "BUY/HOLD"
        assert _verdict(50) == "HOLD"
        assert _verdict(35) == "HOLD/SELL"
        assert _verdict(34) == "SELL"


# ── get_scoring_data_impl ──────────────────────────────────────

class TestGetScoringDataImpl:
    @patch("market_intelligence.scoring.get_technicals_impl")
    @patch("market_intelligence.scoring.get_full_profile_impl")
    def test_normal_stock(self, mock_profile, mock_technicals):
        mock_profile.return_value = {
            "symbol": "AAPL",
            "valuation": {"pe_trailing": 28, "peg_ratio": 1.5},
            "quality": {"roe": 0.15, "debt_to_equity": 100, "current_ratio": 1.5, "profit_margin": 0.20},
            "growth": {"revenue": 380000000000, "net_income": 95000000000},
            "risk": {"beta": 1.2, "insider_pct": 0.08},
        }
        mock_technicals.return_value = {
            "trend": {"above_200dma": True, "above_50dma": True},
            "momentum": {"rsi_14": 55, "macd_bullish": True},
            "strength": {"adx_14": 30},
        }

        result = get_scoring_data_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["blocked"] is False
        assert "pillar_scores" in result
        assert "total_score" in result
        assert "verdict_suggestion" in result
        assert 0 <= result["total_score"] <= 100

    @patch("market_intelligence.scoring.get_technicals_impl")
    @patch("market_intelligence.scoring.get_full_profile_impl")
    def test_deal_breaker_solvency(self, mock_profile, mock_technicals):
        mock_profile.return_value = {
            "symbol": "BAD",
            "quality": {"current_ratio": 0.3, "debt_to_equity": 100},
            "growth": {"revenue": 100, "net_income": 50},
            "risk": {},
            "valuation": {},
        }
        mock_technicals.return_value = {}

        result = get_scoring_data_impl("BAD")
        assert result["blocked"] is True
        assert any("solvency" in db.lower() for db in result["deal_breakers"])

    @patch("market_intelligence.scoring.get_technicals_impl")
    @patch("market_intelligence.scoring.get_full_profile_impl")
    def test_deal_breaker_overleveraged(self, mock_profile, mock_technicals):
        mock_profile.return_value = {
            "symbol": "DEBT",
            "quality": {"current_ratio": 1.5, "debt_to_equity": 600},
            "growth": {"revenue": 100, "net_income": 50},
            "risk": {},
            "valuation": {},
        }
        mock_technicals.return_value = {}

        result = get_scoring_data_impl("DEBT")
        assert result["blocked"] is True
        assert any("overleveraged" in db.lower() for db in result["deal_breakers"])

    @patch("market_intelligence.scoring.get_full_profile_impl")
    def test_profile_error(self, mock_profile):
        mock_profile.return_value = {"symbol": "BAD", "error": "No data found."}
        result = get_scoring_data_impl("BAD")
        assert "error" in result
