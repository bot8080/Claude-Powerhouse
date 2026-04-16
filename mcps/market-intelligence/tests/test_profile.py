"""Tests for profile module — unit tests with mocked yfinance."""
import pytest
from unittest.mock import patch, MagicMock

from market_intelligence.profile import _safe, get_full_profile_impl, get_batch_profiles_impl


# ── _safe helper ────────────────────────────────────────────────

class TestSafe:
    def test_normal_value(self):
        assert _safe({"key": 42}, "key") == 42

    def test_missing_key(self):
        assert _safe({}, "key") is None

    def test_missing_key_with_default(self):
        assert _safe({}, "key", "fallback") == "fallback"

    def test_none_returns_default(self):
        assert _safe({"key": None}, "key", "fallback") == "fallback"

    def test_na_string(self):
        assert _safe({"key": "N/A"}, "key") is None

    def test_empty_string(self):
        assert _safe({"key": ""}, "key") is None

    def test_inf(self):
        assert _safe({"key": float("inf")}, "key") is None

    def test_neg_inf(self):
        assert _safe({"key": float("-inf")}, "key") is None


# ── get_full_profile_impl ──────────────────────────────────────

class TestGetFullProfile:
    @patch("market_intelligence.profile.yf.Ticker")
    def test_successful_profile(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "longName": "Apple Inc.",
            "shortName": "Apple",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "exchange": "NMS",
            "currency": "USD",
            "marketCap": 3000000000000,
            "currentPrice": 180.5,
            "trailingPE": 28.5,
            "returnOnEquity": 0.18,
            "beta": 1.2,
        }
        mock_ticker_cls.return_value = mock_ticker

        result = get_full_profile_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert "error" not in result
        assert result["identity"]["name"] == "Apple Inc."
        assert result["identity"]["sector"] == "Technology"
        assert result["price"]["current"] == 180.5
        assert result["valuation"]["pe_trailing"] == 28.5
        assert result["quality"]["roe"] == 0.18
        assert result["risk"]["beta"] == 1.2

    @patch("market_intelligence.profile.yf.Ticker")
    def test_no_data(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        result = get_full_profile_impl("XYZXYZ")
        assert "error" in result
        assert "No data found" in result["error"]

    @patch("market_intelligence.profile.yf.Ticker")
    def test_exception_handling(self, mock_ticker_cls):
        mock_ticker_cls.side_effect = Exception("Network error")
        result = get_full_profile_impl("AAPL")
        assert "error" in result
        assert "Failed to fetch" in result["error"]

    @patch("market_intelligence.profile.yf.Ticker")
    def test_all_sections_present(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"longName": "Test Co."}
        mock_ticker_cls.return_value = mock_ticker

        result = get_full_profile_impl("TEST")
        expected_keys = ["symbol", "identity", "price", "valuation", "quality",
                         "growth", "analyst", "risk", "dividends", "description"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    @patch("market_intelligence.profile.yf.Ticker")
    def test_fallback_price_to_previous_close(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"longName": "Test", "previousClose": 150.0}
        mock_ticker_cls.return_value = mock_ticker

        result = get_full_profile_impl("TEST")
        assert result["price"]["current"] == 150.0


# ── get_batch_profiles_impl ────────────────────────────────────

class TestGetBatchProfiles:
    @patch("market_intelligence.profile.get_full_profile_impl")
    def test_batch_success(self, mock_profile):
        mock_profile.return_value = {
            "symbol": "AAPL",
            "identity": {"name": "Apple"},
            "price": {}, "valuation": {}, "quality": {},
            "growth": {}, "analyst": {}, "risk": {},
            "dividends": {}, "description": None,
        }
        result = get_batch_profiles_impl(["AAPL", "MSFT"])
        assert result["count"] == 2
        assert result["success_count"] == 2
        assert result["error_count"] == 0

    @patch("market_intelligence.profile.get_full_profile_impl")
    def test_batch_with_error(self, mock_profile):
        def side_effect(sym):
            if sym == "BAD":
                return {"symbol": "BAD", "error": "No data"}
            return {"symbol": sym, "identity": {"name": sym}}
        mock_profile.side_effect = side_effect

        result = get_batch_profiles_impl(["AAPL", "BAD"])
        assert result["count"] == 2
        assert result["error_count"] == 1
        assert result["success_count"] == 1

    @patch("market_intelligence.profile.get_full_profile_impl")
    def test_batch_empty(self, mock_profile):
        result = get_batch_profiles_impl([])
        assert result["count"] == 0
        assert result["success_count"] == 0
