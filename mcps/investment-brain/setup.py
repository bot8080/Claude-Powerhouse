#!/usr/bin/env python3
"""Setup helper for Investment Brain.

Generates the claude_desktop_config.json snippet and verifies the install.

Path rewriting is no longer needed — `config.py` reads from the
MARKET_INTELLIGENCE_CMD env-var, and `mcp_wrapper.py` self-resolves its own
location via Path(__file__). This script just produces the bits a user
still has to copy by hand: the Claude Desktop config snippet and the
env-var line for their shell.

Usage:
    python setup.py
"""

import json
import os
import sys
from pathlib import Path


def detect_paths():
    """Resolve investment-brain and sibling market-intelligence paths."""
    brain_dir = Path(__file__).resolve().parent
    mcps_dir = brain_dir.parent
    market_intel = mcps_dir / "market-intelligence"
    powerhouse_root = mcps_dir.parent

    return {
        "brain_dir": brain_dir,
        "market_intel": market_intel,
        "powerhouse_root": powerhouse_root,
    }


def generate_env_var_line(paths) -> str:
    """Build the MARKET_INTELLIGENCE_CMD value the user should export."""
    market_intel = paths["market_intel"].as_posix()
    return f'uv run --directory {market_intel} python -m market_intelligence'


def generate_claude_config(paths) -> dict:
    """Build the claude_desktop_config.json snippet for both MCP servers."""
    brain_dir = paths["brain_dir"]
    market_intel = paths["market_intel"]

    return {
        "mcpServers": {
            "market-intelligence": {
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    str(market_intel),
                    "python",
                    "-m",
                    "market_intelligence",
                ],
            },
            "investment-brain": {
                "command": "python",
                "args": [str(brain_dir / "mcp_wrapper.py")],
                "env": {
                    "MARKET_INTELLIGENCE_CMD": generate_env_var_line(paths),
                },
            },
        }
    }


def verify_setup(paths) -> bool:
    """Check that all required files are present."""
    brain_dir = paths["brain_dir"]

    checks = [
        ("config.py", brain_dir / "config.py"),
        ("main.py", brain_dir / "main.py"),
        ("mcp_wrapper.py", brain_dir / "mcp_wrapper.py"),
        ("requirements.txt", brain_dir / "requirements.txt"),
        ("market-intelligence (sibling)", paths["market_intel"]),
    ]

    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    all_good = True
    for name, path in checks:
        ok = path.exists()
        status = "OK  " if ok else "FAIL"
        print(f"   [{status}] {name:<40} {path}")
        if not ok:
            all_good = False

    return all_good


def main():
    print("=" * 60)
    print("Investment Brain — Setup Helper")
    print("=" * 60)

    paths = detect_paths()

    print("\nDetected paths:")
    print(f"   investment-brain: {paths['brain_dir']}")
    print(f"   market-intelligence: {paths['market_intel']}")
    print(f"   Claude-Powerhouse root: {paths['powerhouse_root']}")

    if not verify_setup(paths):
        print("\nSome files are missing. Fix the layout before continuing.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("ENV-VAR (add to your shell)")
    print("=" * 60)
    print(f'   export MARKET_INTELLIGENCE_CMD="{generate_env_var_line(paths)}"')
    print('   # On Windows (cmd.exe):  set MARKET_INTELLIGENCE_CMD=...')
    print('   # On Windows (PowerShell): $env:MARKET_INTELLIGENCE_CMD="..."')

    print("\n" + "=" * 60)
    print("CLAUDE DESKTOP CONFIG SNIPPET")
    print("=" * 60)
    config = generate_claude_config(paths)
    print(json.dumps(config, indent=2))

    snippet_file = paths["powerhouse_root"] / "claude_desktop_config_snippet.json"
    snippet_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"\nSaved snippet to: {snippet_file}")

    appdata = os.environ.get("APPDATA", "")
    if appdata:
        target = Path(appdata) / "Claude" / "claude_desktop_config.json"
        print(f"\nMerge the snippet above into: {target}")
    else:
        print("\nMerge the snippet above into your claude_desktop_config.json.")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("   1. pip install -r requirements.txt")
    print("   2. Export MARKET_INTELLIGENCE_CMD (see above) or skip for yfinance-only mode")
    print("   3. Merge the snippet into claude_desktop_config.json")
    print("   4. Restart Claude Desktop")
    print("   5. Test: python main.py analyze AAPL")
    print("=" * 60)


if __name__ == "__main__":
    main()
