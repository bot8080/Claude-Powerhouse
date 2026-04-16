"""Tests for resolver module — unit tests with mocked yfinance."""
import pytest
from unittest.mock import patch, MagicMock

from market_intelligence.resolver import (
    _classify_market,
    _build_resolved,
    _try_ticker,
    _try_search,
    _resolve_single,
    resolve_tickers_impl,
)


# ── _classify_market ────────────────────────────────────────────

class TestClassifyMarket:
    def test_india_nse(self):
        assert _classify_market({"exchange": "NSI", "currency": "INR"}) == ("India", "INR")

    def test_india_bse(self):
        assert _classify_market({"exchange": "BSE", "currency": "INR"}) == ("India", "INR")

    def test_canada_tsx(self):
        assert _classify_market({"exchange": "TOR", "currency": "CAD"}) == ("Canada", "CAD")

    def test_us_default(self):
        assert _classify_market({"exchange": "NMS", "currency": "USD"}) == ("US", "USD")

    def test_empty(self):
        assert _classify_market({}) == ("US", "USD")


# ── _build_resolved ────────────────────────────────────────────

class TestBuildResolved:
    def test_basic(self):
        info = {"longName": "Apple Inc.", "exchange": "NMS", "currency": "USD"}
        result = _build_resolved("AAPL", "AAPL", info)
        assert result["input"] == "AAPL"
        assert result["symbol"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["market"] == "US"

    def test_fallback_to_shortname(self):
        info = {"shortName": "Apple", "exchange": "NMS", "currency": "USD"}
        result = _build_resolved("AAPL", "AAPL", info)
        assert result["name"] == "Apple"


# ── _try_ticker ─────────────────────────────────────────────────

class TestTryTicker:
    @patch("market_intelligence.resolver.yf.Ticker")
    def test_valid_ticker(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"longName": "Apple Inc."}
        mock_ticker_cls.return_value = mock_ticker
        result = _try_ticker("AAPL")
        assert result is not None
        assert result["longName"] == "Apple Inc."

    @patch("market_intelligence.resolver.yf.Ticker")
    def test_invalid_ticker(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker
        result = _try_ticker("XYZXYZ")
        assert result is None

    @patch("market_intelligence.resolver.yf.Ticker")
    def test_exception(self, mock_ticker_cls):
        mock_ticker_cls.side_effect = Exception("network error")
        result = _try_ticker("AAPL")
        assert result is None


# ── _try_search ─────────────────────────────────────────────────

class TestTrySearch:
    @patch("market_intelligence.resolver.yf.Search")
    def test_search_returns_results(self, mock_search_cls):
        mock_search = MagicMock()
        mock_search.quotes = [{"symbol": "AAPL"}]
        mock_search_cls.return_value = mock_search
        result = _try_search("Apple")
        assert len(result) == 1
        assert result[0]["symbol"] == "AAPL"

    @patch("market_intelligence.resolver.yf.Search")
    def test_search_empty(self, mock_search_cls):
        mock_search = MagicMock()
        mock_search.quotes = []
        mock_search_cls.return_value = mock_search
        result = _try_search("xyznonexistent")
        assert result == []

    @patch("market_intelligence.resolver.yf.Search")
    def test_search_attribute_error(self, mock_search_cls):
        mock_search_cls.side_effect = AttributeError
        result = _try_search("Apple")
        assert result == []


# ── _resolve_single ─────────────────────────────────────────────

class TestResolveSingle:
    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_direct_match(self, mock_try_ticker, mock_try_search):
        mock_try_ticker.return_value = {"longName": "Apple Inc.", "exchange": "NMS", "currency": "USD"}
        result = _resolve_single("AAPL")
        assert "resolved" in result
        assert result["resolved"]["symbol"] == "AAPL"

    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_ns_suffix(self, mock_try_ticker, mock_try_search):
        # Direct fails, .NS succeeds
        mock_try_ticker.side_effect = [None, {"longName": "Reliance", "exchange": "NSI", "currency": "INR"}]
        result = _resolve_single("RELIANCE")
        assert "resolved" in result
        assert result["resolved"]["symbol"] == "RELIANCE.NS"

    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_to_suffix(self, mock_try_ticker, mock_try_search):
        # Direct fails, .NS fails, .TO succeeds
        mock_try_ticker.side_effect = [None, None, {"longName": "Shopify", "exchange": "TOR", "currency": "CAD"}]
        result = _resolve_single("SHOP")
        assert "resolved" in result
        assert result["resolved"]["symbol"] == "SHOP.TO"

    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_search_single_result(self, mock_try_ticker, mock_try_search):
        # Direct, .NS, .TO all fail; search returns single result
        mock_try_ticker.side_effect = [None, None, None, {"longName": "Nvidia", "exchange": "NMS", "currency": "USD"}]
        mock_try_search.return_value = [{"symbol": "NVDA"}]
        result = _resolve_single("Nvidia")
        assert "resolved" in result
        assert result["resolved"]["symbol"] == "NVDA"

    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_search_ambiguous(self, mock_try_ticker, mock_try_search):
        mock_try_ticker.side_effect = [None, None, None]
        mock_try_search.return_value = [{"symbol": "TATA.NS"}, {"symbol": "TCS.NS"}, {"symbol": "TATAMOTORS.NS"}]
        result = _resolve_single("TATA")
        assert "ambiguous" in result
        assert len(result["ambiguous"]["candidates"]) == 3

    @patch("market_intelligence.resolver._try_search")
    @patch("market_intelligence.resolver._try_ticker")
    def test_total_failure(self, mock_try_ticker, mock_try_search):
        mock_try_ticker.return_value = None
        mock_try_search.return_value = []
        result = _resolve_single("XYZABC123")
        assert "failed" in result


# ── resolve_tickers_impl ────────────────────────────────────────

class TestResolveTickersImpl:
    @patch("market_intelligence.resolver._resolve_single")
    def test_mixed_results(self, mock_resolve):
        mock_resolve.side_effect = [
            {"resolved": {"input": "AAPL", "symbol": "AAPL", "name": "Apple", "exchange": "NMS", "market": "US", "currency": "USD"}},
            {"ambiguous": {"input": "TATA", "candidates": ["TATA.NS", "TCS.NS"], "reason": "Multiple matches"}},
            {"failed": {"input": "XYZ", "reason": "No match"}},
        ]
        result = resolve_tickers_impl(["AAPL", "TATA", "XYZ"])
        assert len(result["resolved"]) == 1
        assert len(result["ambiguous"]) == 1
        assert len(result["failed"]) == 1

    @patch("market_intelligence.resolver._resolve_single")
    def test_empty_input(self, mock_resolve):
        result = resolve_tickers_impl([])
        assert result == {"resolved": [], "ambiguous": [], "failed": []}
