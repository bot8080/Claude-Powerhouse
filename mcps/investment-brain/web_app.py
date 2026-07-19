"""Web App - FastAPI + simple HTML UI for Oracle server deployment.

Lightweight, no React, no heavy JS. Pure HTML + vanilla JS.
Serves the portfolio dashboard via browser.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
import os

from config import DATA_DIR
from portfolio_db import PortfolioDB
from paper_trading import PaperTradingEngine
from data_fetcher import DataFetcher
from deal_breaker import check_deal_breakers
from scorer import score_stock
from prompt_builder import PromptBuilder

app = FastAPI(title="Investment Brain", version="2.0")

# ─── Models ───
class AnalyzeRequest(BaseModel):
    ticker: str
    market: str = "US"

class ScreenRequest(BaseModel):
    tickers: List[str]
    pe_max: float = 25
    roe_min: float = 15
    sector: Optional[str] = None

class PaperTradeRequest(BaseModel):
    ticker: str
    shares: float
    price: float
    action: str = "BUY"
    sector: Optional[str] = None
    account: str = "TFSA"
    stop_loss: Optional[float] = None
    target: Optional[float] = None

# ─── HTML UI ───
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Brain</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #38bdf8; margin-bottom: 20px; font-size: 24px; }
        .tabs { display: flex; gap: 4px; background: #1e293b; padding: 4px; border-radius: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 8px 16px; border-radius: 6px; border: none; background: transparent; color: #94a3b8; cursor: pointer; font-size: 13px; }
        .tab.active { background: #334155; color: #f8fafc; }
        .card { background: #1e293b; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
        .card-title { font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; padding: 8px; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155; font-size: 11px; text-transform: uppercase; }
        td { padding: 8px; border-bottom: 1px solid #334155; }
        .btn { padding: 6px 12px; border-radius: 6px; border: none; cursor: pointer; font-size: 12px; font-weight: 600; background: #0ea5e9; color: #fff; }
        .btn-ghost { background: #334155; color: #e2e8f0; }
        .input { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 6px 10px; border-radius: 6px; font-size: 13px; width: 100%; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
        .stat-box { background: #0f172a; padding: 12px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 20px; font-weight: 700; }
        .stat-label { font-size: 11px; color: #94a3b8; margin-top: 4px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .score-ring { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; border: 2px solid; }
        .prompt-box { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Investment Brain</h1>

        <div class="tabs">
            <button class="tab active" onclick="showTab('analyze')">Analyze</button>
            <button class="tab" onclick="showTab('screen')">Screener</button>
            <button class="tab" onclick="showTab('portfolio')">Portfolio</button>
            <button class="tab" onclick="showTab('paper')">Paper Trading</button>
            <button class="tab" onclick="showTab('prompt')">Claude Prompt</button>
        </div>

        <!-- Analyze Tab -->
        <div id="analyze" class="tab-content">
            <div class="card">
                <div class="card-title">Analyze Stock</div>
                <div class="grid-3">
                    <input type="text" id="analyze-ticker" class="input" placeholder="Ticker (e.g., TSM)">
                    <select id="analyze-market" class="input">
                        <option value="US">US</option>
                        <option value="CA">CA</option>
                        <option value="IN">IN</option>
                    </select>
                    <button class="btn" onclick="analyzeStock()">Analyze</button>
                </div>
                <div id="analyze-result" style="margin-top: 16px;"></div>
            </div>
        </div>

        <!-- Screen Tab -->
        <div id="screen" class="tab-content hidden">
            <div class="card">
                <div class="card-title">Stock Screener</div>
                <div class="grid-3">
                    <input type="text" id="screen-tickers" class="input" placeholder="Tickers (comma-separated)">
                    <input type="number" id="screen-pe" class="input" placeholder="Max PE" value="25">
                    <input type="number" id="screen-roe" class="input" placeholder="Min ROE %" value="15">
                </div>
                <button class="btn" style="margin-top: 12px;" onclick="runScreener()">Screen</button>
                <div id="screen-result" style="margin-top: 16px;"></div>
            </div>
        </div>

        <!-- Portfolio Tab -->
        <div id="portfolio" class="tab-content hidden">
            <div class="card">
                <div class="card-title">Portfolio Holdings</div>
                <div id="portfolio-data"></div>
            </div>
        </div>

        <!-- Paper Tab -->
        <div id="paper" class="tab-content hidden">
            <div class="card">
                <div class="card-title">New Paper Trade</div>
                <div class="grid-3">
                    <select id="paper-action" class="input">
                        <option value="BUY">BUY</option>
                        <option value="SELL">SELL</option>
                    </select>
                    <input type="text" id="paper-ticker" class="input" placeholder="Ticker">
                    <input type="number" id="paper-shares" class="input" placeholder="Shares">
                    <input type="number" id="paper-price" class="input" placeholder="Price">
                    <input type="text" id="paper-sector" class="input" placeholder="Sector (opt)">
                    <button class="btn" onclick="paperTrade()">Execute</button>
                </div>
                <div id="paper-result" style="margin-top: 16px;"></div>
            </div>
            <div class="card">
                <div class="card-title">Open Positions</div>
                <div id="paper-positions"></div>
            </div>
        </div>

        <!-- Prompt Tab -->
        <div id="prompt" class="tab-content hidden">
            <div class="card">
                <div class="card-title">Latest Claude Prompt</div>
                <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px;">
                    Copy this entire block and paste into Claude Desktop. Claude will format it per your rules.
                </p>
                <div id="claude-prompt" class="prompt-box">Run an analysis to generate a prompt...</div>
                <button class="btn" style="margin-top: 12px;" onclick="copyPrompt()">Copy to Clipboard</button>
            </div>
        </div>
    </div>

    <script>
        let latestPrompt = "";

        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(tabId).classList.remove('hidden');
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');
            if (tabId === 'portfolio') loadPortfolio();
            if (tabId === 'paper') loadPaperPositions();
        }

        async function analyzeStock() {
            const ticker = document.getElementById('analyze-ticker').value;
            const market = document.getElementById('analyze-market').value;
            if (!ticker) return;

            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ticker, market})
            });
            const data = await res.json();

            let html = `<div class="grid-3">`;
            html += `<div class="stat-box"><div class="stat-value" style="color:#22c55e">${data.scores?.fundamentals?.score}/35</div><div class="stat-label">Fundamentals</div></div>`;
            html += `<div class="stat-box"><div class="stat-value" style="color:#38bdf8">${data.scores?.technicals?.score}/35</div><div class="stat-label">Technicals</div></div>`;
            html += `<div class="stat-box"><div class="stat-value" style="color:#a855f7">${data.scores?.smart_money?.score}/30</div><div class="stat-label">Smart Money</div></div>`;
            html += `</div>`;
            html += `<div style="margin-top:12px;font-size:18px;font-weight:700">Total: ${data.scores?.total}/100 | Verdict: <span style="color:${data.scores?.verdict === 'BUY' ? '#22c55e' : '#eab308'}">${data.scores?.verdict}</span></div>`;
            html += `<div style="margin-top:8px;color:#94a3b8">Account: ${data.scores?.account} | Stop: $${data.scores?.stop_loss}</div>`;

            document.getElementById('analyze-result').innerHTML = html;
            latestPrompt = data.prompt;
            document.getElementById('claude-prompt').textContent = data.prompt;
        }

        async function runScreener() {
            const tickers = document.getElementById('screen-tickers').value.split(',').map(s => s.trim()).filter(Boolean);
            const pe = parseFloat(document.getElementById('screen-pe').value);
            const roe = parseFloat(document.getElementById('screen-roe').value);

            const res = await fetch('/api/screen', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tickers: tickers.length ? tickers : ["AAPL","MSFT","NVDA","TSM","ASML"], pe_max: pe, roe_min: roe})
            });
            const data = await res.json();

            let html = `<table><thead><tr><th>Rank</th><th>Ticker</th><th>Score</th><th>Verdict</th><th>PE</th><th>ROE</th></tr></thead><tbody>`;
            data.results?.forEach((r, i) => {
                html += `<tr><td>#${i+1}</td><td><b>${r.ticker}</b></td><td>${r.total}/100</td><td><span class="badge" style="background:${r.verdict==='BUY'?'#22c55e22':'#eab30822'};color:${r.verdict==='BUY'?'#22c55e':'#eab308'}">${r.verdict}</span></td><td>${r.pe?.toFixed(1)||'-'}</td><td>${r.roe?.toFixed(1)||'-'}%</td></tr>`;
            });
            html += `</tbody></table>`;
            document.getElementById('screen-result').innerHTML = html;
            latestPrompt = data.prompt;
            document.getElementById('claude-prompt').textContent = data.prompt;
        }

        async function loadPortfolio() {
            const res = await fetch('/api/portfolio');
            const data = await res.json();
            let html = `<table><thead><tr><th>Ticker</th><th>Shares</th><th>Price</th><th>Value</th><th>Score</th><th>Verdict</th></tr></thead><tbody>`;
            data.holdings?.forEach(h => {
                const val = (h.price || 0) * (h.shares || 0);
                const score = (h.fund_score||0) + (h.tech_score||0) + (h.sm_score||0);
                html += `<tr><td><b>${h.ticker}</b><br><span style="font-size:11px;color:#94a3b8">${h.name||''}</span></td><td>${h.shares||0}</td><td>$${h.price||0}</td><td>$${val.toFixed(2)}</td><td>${score}/100</td><td>${h.verdict||'HOLD'}</td></tr>`;
            });
            html += `</tbody></table>`;
            document.getElementById('portfolio-data').innerHTML = html;
        }

        async function paperTrade() {
            const action = document.getElementById('paper-action').value;
            const ticker = document.getElementById('paper-ticker').value;
            const shares = parseFloat(document.getElementById('paper-shares').value);
            const price = parseFloat(document.getElementById('paper-price').value);
            const sector = document.getElementById('paper-sector').value;

            const res = await fetch('/api/paper-trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action, ticker, shares, price, sector})
            });
            const data = await res.json();
            document.getElementById('paper-result').innerHTML = data.success
                ? `<div style="color:#22c55e">✅ ${data.message}</div>`
                : `<div style="color:#ef4444">❌ ${data.errors?.join(', ')}</div>`;
            loadPaperPositions();
        }

        async function loadPaperPositions() {
            const res = await fetch('/api/paper-positions');
            const data = await res.json();
            let html = `<table><thead><tr><th>Ticker</th><th>Shares</th><th>Entry</th><th>Current</th><th>P&L</th><th>Stop</th></tr></thead><tbody>`;
            data.positions?.forEach(p => {
                const current = p.price || p.entry;
                const pnl = ((current - p.entry) / p.entry * 100).toFixed(1);
                html += `<tr><td><b>${p.ticker}</b></td><td>${p.shares}</td><td>$${p.entry}</td><td>$${current}</td><td style="color:${pnl>=0?'#22c55e':'#ef4444'}">${pnl>=0?'+':''}${pnl}%</td><td>$${p.stop_loss||'-'}</td></tr>`;
            });
            html += `</tbody></table>`;
            html += `<div style="margin-top:12px" class="grid-3"><div class="stat-box"><div class="stat-value" style="color:#38bdf8">$${data.cash?.toFixed(0)||0}</div><div class="stat-label">Cash</div></div><div class="stat-box"><div class="stat-value" style="color:#a855f7">$${data.open_value?.toFixed(0)||0}</div><div class="stat-label">Positions</div></div><div class="stat-box"><div class="stat-value" style="color:${(data.total_pnl||0)>=0?'#22c55e':'#ef4444'}">$${data.total_pnl?.toFixed(0)||0}</div><div class="stat-label">Total P&L</div></div></div>`;
            document.getElementById('paper-positions').innerHTML = html;
        }

        function copyPrompt() {
            navigator.clipboard.writeText(latestPrompt);
            alert('Prompt copied! Paste into Claude Desktop.');
        }
    </script>
</body>
</html>
"""

# ─── API Routes ───

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(content=HTML_PAGE)

@app.post("/api/analyze")
def api_analyze(req: AnalyzeRequest):
    try:
        with DataFetcher() as fetcher:
            data = fetcher.get_stock_data(req.ticker.upper(), req.market)
            if not data:
                raise HTTPException(404, f"Could not fetch data for {req.ticker}")

            db = check_deal_breakers(data)
            if db["blocked"]:
                return {"blocked": True, "reasons": db["reasons"], "evidence": db["evidence"]}

            sector = data.get("profile", {}).get("identity", {}).get("sector", "")
            scores = score_stock(data, sector=sector)
            prompt = PromptBuilder.build_single_stock(data, scores)

            return {
                "ticker": req.ticker.upper(),
                "scores": scores,
                "prompt": prompt,
                "dashboard_json": PromptBuilder.build_dashboard_json(data, scores),
            }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/screen")
def api_screen(req: ScreenRequest):
    try:
        with DataFetcher() as fetcher:
            results = []
            for t in req.tickers:
                data = fetcher.get_stock_data(t)
                if not data:
                    continue
                db = check_deal_breakers(data)
                if db["blocked"]:
                    continue
                sector = data.get("profile", {}).get("identity", {}).get("sector", "")
                if req.sector and sector != req.sector:
                    continue
                scores = score_stock(data, sector=sector)
                raw = scores["fundamentals"]["raw"]
                if raw.get("pe") and raw["pe"] > req.pe_max:
                    continue
                if raw.get("roe") and raw["roe"] < req.roe_min:
                    continue
                results.append({"data": data, "scores": scores, "ticker": t})

            results.sort(key=lambda x: x["scores"]["total"], reverse=True)

            criteria = f"PE < {req.pe_max}, ROE > {req.roe_min}%"
            if req.sector:
                criteria += f", Sector = {req.sector}"

            prompt = PromptBuilder.build_screener(results, criteria, len(req.tickers))

            return {
                "results": [
                    {
                        "ticker": r["ticker"],
                        "name": r["data"].get("profile", {}).get("identity", {}).get("name", ""),
                        "total": r["scores"]["total"],
                        "verdict": r["scores"]["verdict"],
                        "pe": r["scores"]["fundamentals"]["raw"].get("pe"),
                        "roe": r["scores"]["fundamentals"]["raw"].get("roe"),
                    }
                    for r in results[:10]
                ],
                "prompt": prompt,
            }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/portfolio")
def api_portfolio():
    db = PortfolioDB()
    return {"holdings": db.get_portfolio()}

@app.post("/api/paper-trade")
def api_paper_trade(req: PaperTradeRequest):
    engine = PaperTradingEngine(PortfolioDB())
    if req.action == "BUY":
        result = engine.buy(
            ticker=req.ticker,
            shares=req.shares,
            entry=req.price,
            sector=req.sector or "",
            account=req.account,
            stop_loss=req.stop_loss,
            target=req.target,
        )
    else:
        result = engine.sell(req.ticker, req.shares, req.price)

    if result["success"]:
        return {"success": True, "message": f"{req.action} {req.shares} shares of {req.ticker} @ ${req.price}"}
    else:
        return {"success": False, "errors": result.get("errors", [])}

@app.get("/api/paper-positions")
def api_paper_positions():
    engine = PaperTradingEngine(PortfolioDB())
    return {
        "positions": engine.get_positions(),
        "cash": engine.get_cash(),
        "open_value": engine.get_portfolio_value(),
        "total_value": engine.get_total_value(),
        "total_pnl": engine.get_summary()["total_pnl"],
    }

@app.get("/api/export")
def api_export():
    db = PortfolioDB()
    return db.get_all_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
