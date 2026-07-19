"""MCP Bridge - Connects to local MCP server via stdio JSON-RPC.

No external dependencies. Pure Python subprocess + JSON.
"""

import json
import os
import shlex
import subprocess
import threading
import time
import uuid
from typing import Any, Dict, List, Optional


class MCPClient:
    """Lightweight MCP client using JSON-RPC over stdio."""

    def __init__(self, command: str):
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._pending: Dict[str, Any] = {}
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False

    def connect(self) -> bool:
        """Start the MCP server subprocess."""
        try:
            # shell=False for security (no shell injection); split command string
            # into argv. stderr=DEVNULL prevents deadlock when server emits many
            # warnings (e.g. yfinance deprecation notices) that would fill the
            # stderr pipe buffer with no reader on our side.
            argv = shlex.split(self.command, posix=(os.name != "nt"))
            self.process = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                shell=False,
            )
            self._running = True
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()
            time.sleep(0.5)  # Let server initialize
            return self._send_initialize()
        except Exception as e:
            print(f"[MCP] Failed to connect: {e}")
            return False

    def _send_initialize(self) -> bool:
        """Send initialize handshake."""
        result = self.call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "investment-brain", "version": "1.0.0"}
        })
        return result is not None

    def _read_loop(self):
        """Background thread reading stdout from MCP server."""
        while self._running and self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if not line:
                    continue
                msg = json.loads(line)
                if "id" in msg and msg["id"] in self._pending:
                    self._pending[msg["id"]] = msg
            except Exception:
                pass

    def call(self, method: str, params: Optional[Dict] = None, timeout: float = 15.0) -> Any:
        """Call an MCP tool and return the result."""
        if not self.process or self.process.poll() is not None:
            return None

        req_id = str(uuid.uuid4())
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }

        with self._lock:
            self._pending[req_id] = None

        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
        except Exception as e:
            print(f"[MCP] Write error: {e}")
            return None

        start = time.time()
        while time.time() - start < timeout:
            with self._lock:
                response = self._pending.get(req_id)
                if response is not None:
                    del self._pending[req_id]
                    if "error" in response:
                        print(f"[MCP] Error: {response['error']}")
                        return None
                    return response.get("result")
            time.sleep(0.05)

        with self._lock:
            self._pending.pop(req_id, None)
        print(f"[MCP] Timeout calling {method}")
        return None

    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call a tool by name (handles both direct and tools/call methods)."""
        # Try modern tools/call first
        result = self.call("tools/call", {"name": tool_name, "arguments": arguments})
        if result is not None:
            return result
        # Fallback to direct method call
        return self.call(tool_name, arguments)

    @staticmethod
    def _unwrap(result: Any) -> Any:
        """Extract the JSON payload from an MCP tool-call result envelope.

        MCP servers return results as:
            {"content": [{"type": "text", "text": "<json string>"}]}

        Callers need the parsed JSON payload inside `text`, not the envelope.
        Returns None if the result shape is unexpected or JSON parsing fails.
        """
        if not isinstance(result, dict):
            return None
        content = result.get("content")
        if not isinstance(content, list) or not content:
            # Tool may have returned a bare dict (no envelope) — pass through.
            return result if "content" not in result else None
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text")
                if t:
                    text_parts.append(t)
        if not text_parts:
            return None
        joined = "".join(text_parts)
        try:
            return json.loads(joined)
        except (json.JSONDecodeError, ValueError):
            return joined

    def disconnect(self):
        """Clean shutdown."""
        self._running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()


class MCPDataFetcher:
    """High-level data fetcher using MCP client."""

    def __init__(self, command: str):
        self.client = MCPClient(command)
        self.connected = False

    def connect(self) -> bool:
        self.connected = self.client.connect()
        return self.connected

    def disconnect(self):
        self.client.disconnect()
        self.connected = False

    def resolve_tickers(self, queries: List[str]) -> List[Dict]:
        """Resolve company names to tickers."""
        if not self.connected:
            return []
        result = self.client.call_tool("resolve_tickers", {"queries": queries})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, list) else []

    def get_scoring_data(self, symbol: str) -> Optional[Dict]:
        """Fetch full scoring data for a ticker."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_scoring_data", {"symbol": symbol})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None

    def get_batch_profiles(self, symbols: List[str]) -> List[Dict]:
        """Fetch batch profiles for multiple tickers."""
        if not self.connected:
            return []
        result = self.client.call_tool("get_batch_profiles", {"symbols": symbols})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, list) else []

    def get_institutional_activity(self, symbol: str) -> Optional[Dict]:
        """Fetch institutional/insider data."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_institutional_activity", {"symbol": symbol})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None

    def get_technicals(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """Fetch technical indicators."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_technicals", {"symbol": symbol, "period": period})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None

    def get_us_macro(self) -> Optional[Dict]:
        """Fetch US macro data."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_us_macro", {})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None

    def get_nifty_valuation(self) -> Optional[Dict]:
        """Fetch India Nifty valuation."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_nifty_valuation", {})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None

    def get_fii_dii_flows(self, days: int = 20) -> Optional[Dict]:
        """Fetch FII/DII flows."""
        if not self.connected:
            return None
        result = self.client.call_tool("get_fii_dii_flows", {"days": days})
        unwrapped = MCPClient._unwrap(result)
        return unwrapped if isinstance(unwrapped, dict) else None
