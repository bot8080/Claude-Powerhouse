#!/usr/bin/env python3
"""Setup script for Investment Brain MCP.

Run this after extracting the investment_brain folder.
It will:
1. Detect your Windows username and paths
2. Move investment_brain to Claude-Powerhouse/mcps/
3. Update all path references automatically
4. Generate your claude_desktop_config.json snippet
5. Verify the setup

Usage:
    python setup.py
"""

import json
import os
import shutil
import sys
from pathlib import Path


def detect_paths():
    """Auto-detect Windows paths."""
    user = os.environ.get("USERNAME", os.environ.get("USER", "abhik"))
    home = Path.home()

    # Possible locations for Claude-Powerhouse
    candidates = [
        home / "OneDrive" / "Documents" / "Projects" / "Claude-Powerhouse",
        home / "Documents" / "Projects" / "Claude-Powerhouse",
        home / "Projects" / "Claude-Powerhouse",
    ]

    claude_powerhouse = None
    for c in candidates:
        if c.exists():
            claude_powerhouse = c
            break

    if not claude_powerhouse:
        print("Could not find Claude-Powerhouse folder.")
        print("   Searched:")
        for c in candidates:
            print(f"   - {c}")

        custom = input("\nEnter full path to Claude-Powerhouse folder: ").strip()
        claude_powerhouse = Path(custom)
        if not claude_powerhouse.exists():
            print(f"Path does not exist: {claude_powerhouse}")
            sys.exit(1)

    # Find current investment_brain location
    current_brain = Path(__file__).parent.resolve()

    return {
        "user": user,
        "home": home,
        "claude_powerhouse": claude_powerhouse,
        "current_brain": current_brain,
        "target_brain": claude_powerhouse / "mcps" / "investment-brain",
        "market_intel": claude_powerhouse / "mcps" / "market-intelligence",
    }


def move_folder(paths):
    """Move investment_brain to target location."""
    src = paths["current_brain"]
    dst = paths["target_brain"]

    if src == dst:
        print("Already in correct location.")
        return dst

    if dst.exists():
        print(f"Target already exists: {dst}")
        overwrite = input("   Overwrite? (y/n): ").strip().lower()
        if overwrite == "y":
            shutil.rmtree(dst)
        else:
            print("   Keeping existing. Updating paths only.")
            return dst

    dst.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nMoving folder...")
    print(f"   From: {src}")
    print(f"   To:   {dst}")

    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("data", "__pycache__", "*.pyc"))

    data_src = src / "data"
    data_dst = dst / "data"
    if data_src.exists() and not data_dst.exists():
        shutil.copytree(data_src, data_dst)

    print("Folder moved successfully.")
    return dst


def update_mcp_wrapper(paths):
    """Update BRAIN_DIR in mcp_wrapper.py."""
    file = paths["target_brain"] / "mcp_wrapper.py"
    if not file.exists():
        print(f"{file} not found, skipping.")
        return

    content = file.read_text(encoding="utf-8")

    # Replace BRAIN_DIR line using regex
    import re
    content = re.sub(
        r'BRAIN_DIR = Path\([^)]+\)',
        f'BRAIN_DIR = Path("{paths["target_brain"].as_posix()}")',
        content
    )

    file.write_text(content, encoding="utf-8")
    print("Updated mcp_wrapper.py")


def update_config_py(paths):
    """Update MCP_SERVER_CMD in config.py."""
    file = paths["target_brain"] / "config.py"
    if not file.exists():
        print(f"{file} not found, skipping.")
        return

    content = file.read_text(encoding="utf-8")

    market_intel = paths["market_intel"]
    mcp_cmd = f'uv run --directory {market_intel.as_posix()} python -m market_intelligence'

    # Replace the commented example line
    content = content.replace(
        '# "uv run --directory C:/\\\\Users\\\\abhik',
        f'# "{mcp_cmd}"'
    )

    # Also try to replace any existing MCP_SERVER_CMD default
    import re
    content = re.sub(
        r'(MCP_SERVER_CMD = os\.environ\.get\(\s*"MCP_SERVER_CMD",\s*\n\s*#?\s*)"[^"]*"',
        f'\1"{mcp_cmd}"',
        content
    )

    file.write_text(content, encoding="utf-8")
    print("Updated config.py")


def generate_claude_config(paths):
    """Generate the claude_desktop_config.json snippet."""
    brain_path = paths["target_brain"]
    market_intel_path = paths["market_intel"]

    config = {
        "mcpServers": {
            "market-intelligence": {
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    str(market_intel_path),
                    "python",
                    "-m",
                    "market_intelligence"
                ]
            },
            "investment-brain": {
                "command": "python",
                "args": [
                    str(brain_path / "mcp_wrapper.py")
                ]
            }
        }
    }

    print("\n" + "=" * 60)
    print("ADD THIS TO YOUR claude_desktop_config.json")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    print("=" * 60)

    config_file = paths["claude_powerhouse"] / "claude_desktop_config_snippet.json"
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"\nSaved to: {config_file}")

    appdata = os.environ.get("APPDATA", "")
    if appdata:
        actual_config = Path(appdata) / "Claude" / "claude_desktop_config.json"
        print(f"\nYour actual config file should be at:")
        print(f"   {actual_config}")
        if actual_config.exists():
            print(f"   File exists")
        else:
            print(f"   File not found. Create it if needed.")


def verify_setup(paths):
    """Verify everything is in place."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    checks = [
        ("Investment Brain folder", paths["target_brain"].exists()),
        ("mcp_wrapper.py", (paths["target_brain"] / "mcp_wrapper.py").exists()),
        ("main.py", (paths["target_brain"] / "main.py").exists()),
        ("config.py", (paths["target_brain"] / "config.py").exists()),
        ("market-intelligence MCP", paths["market_intel"].exists()),
    ]

    all_good = True
    for name, ok in checks:
        status = "OK" if ok else "FAIL"
        print(f"   [{status}] {name}")
        if not ok:
            all_good = False

    print("\n" + "=" * 60)
    if all_good:
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("   1. Install requirements: pip install -r requirements.txt")
        print("   2. Update claude_desktop_config.json (see snippet above)")
        print("   3. Restart Claude Desktop")
        print("   4. Test: 'Analyze TSM'")
    else:
        print("SOME CHECKS FAILED")
        print("   Please review the errors above.")
    print("=" * 60)


def main():
    print("=" * 60)
    print("Investment Brain - Setup Script")
    print("=" * 60)

    print("\nDetecting paths...")
    paths = detect_paths()
    print(f"   User: {paths['user']}")
    print(f"   Claude-Powerhouse: {paths['claude_powerhouse']}")
    print(f"   Current brain: {paths['current_brain']}")
    print(f"   Target brain: {paths['target_brain']}")
    print(f"   Market-intel: {paths['market_intel']}")

    print("\nStep 1: Moving folder...")
    move_folder(paths)

    print("\nStep 2: Updating path references...")
    update_mcp_wrapper(paths)
    update_config_py(paths)

    print("\nStep 3: Generating Claude Desktop config...")
    generate_claude_config(paths)

    verify_setup(paths)


if __name__ == "__main__":
    main()
