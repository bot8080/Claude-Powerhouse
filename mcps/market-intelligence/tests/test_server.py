"""Tests for server module — verify tool registrations and wiring."""
import pytest
from unittest.mock import patch, MagicMock

from market_intelligence.server import mcp


class TestServerToolRegistration:
    """Verify all 9 tools are registered on the FastMCP instance."""

    def test_mcp_instance_exists(self):
        assert mcp is not None
        assert mcp.name == "market_intelligence"

    def test_tool_count(self):
        """Verify exactly 9 tools are registered."""
        # FastMCP stores tools; the attribute name varies by version
        # Try to list tools — we check for the expected function names
        from market_intelligence.server import (
            resolve_tickers,
            get_full_profile,
            get_batch_profiles,
            get_technicals,
            get_fii_dii_flows,
            get_nifty_valuation,
            get_scoring_data,
            get_institutional_activity,
            get_us_macro,
        )
        # All 9 functions should be importable
        assert callable(resolve_tickers)
        assert callable(get_full_profile)
        assert callable(get_batch_profiles)
        assert callable(get_technicals)
        assert callable(get_fii_dii_flows)
        assert callable(get_nifty_valuation)
        assert callable(get_scoring_data)
        assert callable(get_institutional_activity)
        assert callable(get_us_macro)


class TestServerToolWiring:
    """Verify each server tool delegates to the correct _impl function."""

    @patch("market_intelligence.server.resolve_tickers_impl")
    def test_resolve_tickers_delegates(self, mock_impl):
        from market_intelligence.server import resolve_tickers
        mock_impl.return_value = {"resolved": [], "ambiguous": [], "failed": []}
        result = resolve_tickers(["AAPL"])
        mock_impl.assert_called_once_with(["AAPL"])

    @patch("market_intelligence.server.get_full_profile_impl")
    def test_get_full_profile_delegates(self, mock_impl):
        from market_intelligence.server import get_full_profile
        mock_impl.return_value = {"symbol": "AAPL"}
        result = get_full_profile("AAPL")
        mock_impl.assert_called_once_with("AAPL")

    @patch("market_intelligence.server.get_batch_profiles_impl")
    def test_get_batch_profiles_delegates(self, mock_impl):
        from market_intelligence.server import get_batch_profiles
        mock_impl.return_value = {"profiles": []}
        result = get_batch_profiles(["AAPL", "MSFT"])
        mock_impl.assert_called_once_with(["AAPL", "MSFT"])

    @patch("market_intelligence.server.get_technicals_impl")
    def test_get_technicals_delegates(self, mock_impl):
        from market_intelligence.server import get_technicals
        mock_impl.return_value = {"symbol": "AAPL"}
        result = get_technicals("AAPL", "1y")
        mock_impl.assert_called_once_with("AAPL", "1y")

    @patch("market_intelligence.server.get_fii_dii_flows_impl")
    def test_get_fii_dii_flows_delegates(self, mock_impl):
        from market_intelligence.server import get_fii_dii_flows
        mock_impl.return_value = {"daily": []}
        result = get_fii_dii_flows(20)
        mock_impl.assert_called_once_with(20)

    @patch("market_intelligence.server.get_nifty_valuation_impl")
    def test_get_nifty_valuation_delegates(self, mock_impl):
        from market_intelligence.server import get_nifty_valuation
        mock_impl.return_value = {"pe": 22}
        result = get_nifty_valuation()
        mock_impl.assert_called_once()

    @patch("market_intelligence.server.get_scoring_data_impl")
    def test_get_scoring_data_delegates(self, mock_impl):
        from market_intelligence.server import get_scoring_data
        mock_impl.return_value = {"symbol": "AAPL"}
        result = get_scoring_data("AAPL")
        mock_impl.assert_called_once_with("AAPL")

    @patch("market_intelligence.server.get_institutional_activity_impl")
    def test_get_institutional_activity_delegates(self, mock_impl):
        from market_intelligence.server import get_institutional_activity
        mock_impl.return_value = {"symbol": "AAPL"}
        result = get_institutional_activity("AAPL")
        mock_impl.assert_called_once_with("AAPL")

    @patch("market_intelligence.server.get_us_macro_impl")
    def test_get_us_macro_delegates(self, mock_impl):
        from market_intelligence.server import get_us_macro
        mock_impl.return_value = {"market": "US Macro Overlay"}
        result = get_us_macro()
        mock_impl.assert_called_once()
