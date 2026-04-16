"""
Live integration tests -- hit real Yahoo Finance API.
These are slow and require internet. Run with:
    uv run pytest tests/test_live_integration.py -v -s --timeout=120

Marked with @pytest.mark.live so they can be easily excluded:
    uv run pytest -m "not live"
"""
import pytest
import json

# Mark all tests in this module as live
pytestmark = pytest.mark.live


class TestLiveResolver:
    def test_resolve_us_ticker(self):
        from market_intelligence.resolver import resolve_tickers_impl
        result = resolve_tickers_impl(["AAPL"])
        assert len(result["resolved"]) == 1
        assert result["resolved"][0]["symbol"] == "AAPL"
        assert result["resolved"][0]["market"] == "US"
        print(f"  [OK] Resolved AAPL -> {result['resolved'][0]}")

    def test_resolve_india_ticker(self):
        from market_intelligence.resolver import resolve_tickers_impl
        result = resolve_tickers_impl(["RELIANCE"])
        resolved = result["resolved"]
        assert len(resolved) >= 1
        sym = resolved[0]["symbol"]
        assert ".NS" in sym or ".BO" in sym or resolved[0]["market"] == "India"
        print(f"  [OK] Resolved RELIANCE -> {sym}")

    def test_resolve_canada_ticker(self):
        from market_intelligence.resolver import resolve_tickers_impl
        result = resolve_tickers_impl(["SHOP"])
        resolved = result["resolved"]
        # SHOP may resolve to US (NYSE) or Canada (.TO)
        assert len(resolved) >= 1
        print(f"  [OK] Resolved SHOP -> {resolved[0]['symbol']}")

    def test_resolve_nonexistent(self):
        from market_intelligence.resolver import resolve_tickers_impl
        result = resolve_tickers_impl(["XYZABC123NONEXIST"])
        assert len(result["failed"]) == 1
        print(f"  [OK] Correctly failed: {result['failed'][0]}")

    def test_resolve_batch(self):
        from market_intelligence.resolver import resolve_tickers_impl
        result = resolve_tickers_impl(["AAPL", "MSFT", "NVDA"])
        assert len(result["resolved"]) == 3
        print(f"  [OK] Batch resolved: {[r['symbol'] for r in result['resolved']]}")


class TestLiveProfile:
    def test_full_profile_aapl(self):
        from market_intelligence.profile import get_full_profile_impl
        result = get_full_profile_impl("AAPL")
        assert "error" not in result
        assert result["identity"]["name"] is not None
        assert result["price"]["current"] is not None
        assert result["valuation"]["pe_trailing"] is not None
        print(f"  [OK] AAPL profile: {result['identity']['name']}, price=${result['price']['current']}")

    def test_full_profile_indian_stock(self):
        from market_intelligence.profile import get_full_profile_impl
        result = get_full_profile_impl("RELIANCE.NS")
        assert "error" not in result
        assert result["identity"]["name"] is not None
        print(f"  [OK] RELIANCE.NS: {result['identity']['name']}")

    def test_batch_profiles(self):
        from market_intelligence.profile import get_batch_profiles_impl
        result = get_batch_profiles_impl(["AAPL", "MSFT"])
        assert result["success_count"] >= 1
        assert result["count"] == 2
        print(f"  [OK] Batch: {result['success_count']}/{result['count']} succeeded")

    def test_invalid_ticker_profile(self):
        from market_intelligence.profile import get_full_profile_impl
        result = get_full_profile_impl("XYZXYZ123")
        assert "error" in result
        print(f"  [OK] Invalid ticker error: {result['error']}")


class TestLiveTechnicals:
    def test_technicals_aapl(self):
        from market_intelligence.technicals import get_technicals_impl
        result = get_technicals_impl("AAPL", "1y")
        assert "error" not in result
        assert result["data_points"] >= 50
        assert result["momentum"]["rsi_14"] is not None
        assert result["signals"]["overall"] in [
            "strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"
        ]
        print(f"  [OK] AAPL technicals: RSI={result['momentum']['rsi_14']}, signal={result['signals']['overall']}")

    def test_technicals_short_period(self):
        from market_intelligence.technicals import get_technicals_impl
        result = get_technicals_impl("AAPL", "1mo")
        # 1 month may not have 50 data points
        if "error" in result:
            assert "Insufficient" in result["error"]
            print(f"  [OK] Correctly handled short period: {result['error']}")
        else:
            print(f"  [OK] 1mo technicals: {result['data_points']} data points")


class TestLiveActivity:
    def test_activity_us_stock(self):
        from market_intelligence.activity import get_institutional_activity_impl
        result = get_institutional_activity_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["market"] == "US/Canada/Other"
        print(f"  [OK] AAPL activity sections: {[k for k in result.keys() if k not in ('symbol', 'market')]}")


class TestLiveScoring:
    def test_scoring_aapl(self):
        from market_intelligence.scoring import get_scoring_data_impl
        result = get_scoring_data_impl("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["blocked"] is False
        assert 0 <= result["total_score"] <= 100
        assert result["verdict_suggestion"] in ["BUY", "BUY/HOLD", "HOLD", "HOLD/SELL", "SELL"]
        print(f"  [OK] AAPL score: {result['total_score']}/100, verdict={result['verdict_suggestion']}")
        for pillar, data in result["pillar_scores"].items():
            print(f"    {pillar}: {data['score']}/{data['max']} -- {data['reason']}")


class TestLiveIndia:
    def test_nifty_valuation(self):
        from market_intelligence.india import get_nifty_valuation_impl
        result = get_nifty_valuation_impl()
        # Should return data from either nsetools or yfinance fallback
        if "error" not in result:
            print(f"  [OK] Nifty valuation via {result.get('source', 'unknown')}")
            if "pe" in result:
                print(f"    PE={result['pe']}, zone={result.get('valuation_zone')}")
        else:
            print(f"  [WARN] Nifty valuation unavailable (expected on some systems): {result['error']}")

    def test_fii_dii_flows(self):
        from market_intelligence.india import get_fii_dii_flows_impl
        result = get_fii_dii_flows_impl(days=5)
        if "error" not in result:
            print(f"  [OK] FII/DII flows: {len(result.get('daily', []))} days, signal={result.get('signal', 'N/A')}")
        else:
            print(f"  [WARN] FII/DII unavailable (expected on some systems): {result['error']}")
