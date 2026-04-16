"""Tests for activity module — insider/institutional activity."""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from market_intelligence.activity import _df_to_records, get_institutional_activity_impl


# ── _df_to_records ──────────────────────────────────────────────

class TestDfToRecords:
    def test_normal_df(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        records = _df_to_records(df, limit=10)
        assert len(records) == 3
        assert records[0]["a"] == "1"

    def test_limit(self):
        df = pd.DataFrame({"a": range(20)})
        records = _df_to_records(df, limit=5)
        assert len(records) == 5

    def test_empty_df(self):
        df = pd.DataFrame()
        records = _df_to_records(df)
        assert records == []

    def test_none_df(self):
        records = _df_to_records(None)
        assert records == []

    def test_with_named_index(self):
        df = pd.DataFrame({"val": [1, 2]}, index=pd.Index(["a", "b"], name="key"))
        records = _df_to_records(df)
        assert len(records) == 2
        assert "key" in records[0]


# ── get_institutional_activity_impl ─────────────────────────────

class TestGetInstitutionalActivity:
    @patch("market_intelligence.activity.yf.Ticker")
    def test_us_stock(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"exchange": "NMS", "currency": "USD"}
        mock_ticker.insider_transactions = pd.DataFrame({
            "Insider": ["John Doe"],
            "Transaction": ["Sale"],
            "Shares": [1000],
        })
        mock_ticker.institutional_holders = pd.DataFrame({
            "Holder": ["Vanguard"],
            "Shares": [10000000],
        })
        mock_ticker.mutualfund_holders = pd.DataFrame({
            "Holder": ["Some Fund"],
            "Shares": [5000000],
        })
        mock_ticker.upgrades_downgrades = pd.DataFrame({
            "Firm": ["Goldman"],
            "ToGrade": ["Buy"],
        })
        mock_ticker.calendar = {"Earnings Date": ["2024-07-25"]}
        mock_ticker.major_holders = pd.DataFrame({
            0: ["2.09%", "75.12%"],
            1: ["% of Shares Held by Insiders", "% of Shares Held by Institutions"],
        })
        mock_ticker_cls.return_value = mock_ticker

        result = get_institutional_activity_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["market"] == "US/Canada/Other"
        assert result["insider_transactions"] is not None
        assert result["institutional_holders"] is not None
        assert result["earnings_calendar"] is not None

    @patch("market_intelligence.activity.yf.Ticker")
    def test_indian_stock(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"exchange": "NSI", "currency": "INR"}
        mock_ticker.insider_transactions = pd.DataFrame()
        mock_ticker.institutional_holders = pd.DataFrame()
        mock_ticker.mutualfund_holders = pd.DataFrame()
        mock_ticker.upgrades_downgrades = pd.DataFrame()
        mock_ticker.calendar = None
        mock_ticker.major_holders = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        result = get_institutional_activity_impl("BEL.NS")
        assert result["market"] == "India"
        assert result["insider_transactions"] is None
        assert "Not available for Indian stocks" in (result.get("insider_transactions_note") or "")

    @patch("market_intelligence.activity.yf.Ticker")
    def test_fetch_error(self, mock_ticker_cls):
        mock_ticker_cls.side_effect = Exception("Network error")
        result = get_institutional_activity_impl("AAPL")
        assert "error" in result

    @patch("market_intelligence.activity.yf.Ticker")
    def test_all_sections_present(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {"exchange": "NMS"}
        # All properties return empty dataframes
        mock_ticker.insider_transactions = pd.DataFrame()
        mock_ticker.institutional_holders = pd.DataFrame()
        mock_ticker.mutualfund_holders = pd.DataFrame()
        mock_ticker.upgrades_downgrades = pd.DataFrame()
        mock_ticker.calendar = {}
        mock_ticker.major_holders = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        result = get_institutional_activity_impl("TEST")
        expected_keys = ["symbol", "market"]
        for key in expected_keys:
            assert key in result
