"""Tests for technicals module — unit + mock tests."""
import math
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from market_intelligence.technicals import (
    _safe_float,
    _rsi_zone,
    _mfi_zone,
    _trend_strength,
    _overall_signal,
    get_technicals_impl,
)


# ── _safe_float ─────────────────────────────────────────────────

class TestSafeFloat:
    def test_normal(self):
        assert _safe_float(42.123) == 42.123

    def test_nan(self):
        assert _safe_float(float("nan")) is None

    def test_inf(self):
        assert _safe_float(float("inf")) is None

    def test_string_number(self):
        assert _safe_float("3.14") == 3.14

    def test_non_numeric(self):
        assert _safe_float("abc") is None

    def test_none(self):
        assert _safe_float(None) is None

    def test_rounding(self):
        assert _safe_float(1.23456789) == 1.2346


# ── _rsi_zone ───────────────────────────────────────────────────

class TestRsiZone:
    def test_oversold(self):
        assert _rsi_zone(25) == "oversold"

    def test_overbought(self):
        assert _rsi_zone(75) == "overbought"

    def test_neutral(self):
        assert _rsi_zone(50) == "neutral"

    def test_boundary_30(self):
        assert _rsi_zone(30) == "neutral"

    def test_boundary_70(self):
        assert _rsi_zone(70) == "neutral"

    def test_none(self):
        assert _rsi_zone(None) == "unknown"


# ── _mfi_zone ───────────────────────────────────────────────────

class TestMfiZone:
    def test_oversold(self):
        assert _mfi_zone(15) == "oversold"

    def test_overbought(self):
        assert _mfi_zone(85) == "overbought"

    def test_neutral(self):
        assert _mfi_zone(50) == "neutral"

    def test_none(self):
        assert _mfi_zone(None) == "unknown"


# ── _trend_strength ─────────────────────────────────────────────

class TestTrendStrength:
    def test_weak(self):
        assert _trend_strength(15) == "weak"

    def test_moderate(self):
        assert _trend_strength(30) == "moderate"

    def test_strong(self):
        assert _trend_strength(45) == "strong"

    def test_none(self):
        assert _trend_strength(None) == "unknown"


# ── _overall_signal ─────────────────────────────────────────────

class TestOverallSignal:
    def test_strong_bullish(self):
        result = _overall_signal(True, True, 55.0, True, 30.0)
        assert result == "strong_bullish"

    def test_bullish(self):
        result = _overall_signal(True, True, 55.0, False, 15.0)
        assert result == "bullish"

    def test_neutral(self):
        result = _overall_signal(True, False, 40.0, False, 15.0)
        assert result == "neutral"

    def test_bearish(self):
        result = _overall_signal(False, False, 40.0, True, 15.0)
        assert result == "bearish"

    def test_strong_bearish(self):
        result = _overall_signal(False, False, 80.0, False, 10.0)
        assert result == "strong_bearish"


# ── get_technicals_impl ────────────────────────────────────────

class TestGetTechnicalsImpl:
    def _make_df(self, n=250):
        """Create a realistic-looking OHLCV DataFrame."""
        np.random.seed(42)
        dates = pd.date_range(end="2024-12-31", periods=n, freq="B")
        base = 100 + np.cumsum(np.random.randn(n) * 0.5)
        df = pd.DataFrame({
            "Open": base + np.random.randn(n) * 0.2,
            "High": base + abs(np.random.randn(n)) * 1.5,
            "Low": base - abs(np.random.randn(n)) * 1.5,
            "Close": base,
            "Volume": np.random.randint(1_000_000, 50_000_000, n),
        }, index=dates)
        return df

    @patch("market_intelligence.technicals.yf.Ticker")
    def test_full_output_structure(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._make_df(250)
        mock_ticker_cls.return_value = mock_ticker

        result = get_technicals_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert "error" not in result

        # Check all top-level sections
        for key in ["trend", "momentum", "volatility", "strength", "volume", "signals"]:
            assert key in result, f"Missing section: {key}"

        # Check trend fields
        assert "sma_50" in result["trend"]
        assert "sma_200" in result["trend"]
        assert isinstance(result["trend"]["above_50dma"], bool)

        # Check momentum fields
        assert "rsi_14" in result["momentum"]
        assert result["momentum"]["rsi_zone"] in ["oversold", "overbought", "neutral", "unknown"]

        # Check signals
        assert result["signals"]["overall"] in [
            "strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"
        ]
        assert result["signals"]["current_price"] is not None

    @patch("market_intelligence.technicals.yf.Ticker")
    def test_insufficient_data(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._make_df(30)  # < 50 required
        mock_ticker_cls.return_value = mock_ticker

        result = get_technicals_impl("AAPL")
        assert "error" in result
        assert "Insufficient" in result["error"]

    @patch("market_intelligence.technicals.yf.Ticker")
    def test_exception(self, mock_ticker_cls):
        mock_ticker_cls.side_effect = Exception("API down")
        result = get_technicals_impl("AAPL")
        assert "error" in result

    @patch("market_intelligence.technicals.yf.Ticker")
    def test_no_200dma_with_short_data(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._make_df(100)  # >50 but <200
        mock_ticker_cls.return_value = mock_ticker

        result = get_technicals_impl("AAPL")
        assert result["trend"]["sma_200"] is None
        assert result["trend"]["above_200dma"] is False

    @patch("market_intelligence.technicals.yf.Ticker")
    def test_stop_loss_calculated(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self._make_df(250)
        mock_ticker_cls.return_value = mock_ticker

        result = get_technicals_impl("AAPL")
        assert result["signals"]["suggested_stop_loss"] is not None
        assert result["signals"]["suggested_stop_loss"] < result["signals"]["current_price"]
