#!/usr/bin/env bash
# Run once before first dispatch to verify the environment is ready.
# Usage: bash .internal/.powerhouse/setup.sh

set -euo pipefail

PASS="✓"
FAIL="✗"
ERRORS=0

check() {
  local label="$1"
  local ok="$2"
  if [ "$ok" = "1" ]; then
    echo "  $PASS  $label"
  else
    echo "  $FAIL  $label"
    ERRORS=$((ERRORS + 1))
  fi
}

echo ""
echo "=== Powerhouse dispatch pre-flight ==="
echo ""

# 1. opencode binary
if command -v opencode &>/dev/null; then
  check "opencode installed ($(opencode --version 2>/dev/null | head -1 || echo 'unknown version'))" 1
else
  check "opencode installed — run: curl -fsSL https://opencode.ai/install | bash" 0
fi

# 2. OpenRouter auth
if opencode auth list 2>/dev/null | grep -qi openrouter; then
  check "OpenRouter auth present" 1
else
  check "OpenRouter auth missing — run: opencode auth login" 0
fi

# 3. follow-ticket command
if [ -f "$(git rev-parse --show-toplevel 2>/dev/null)/.opencode/commands/follow-ticket.md" ]; then
  check ".opencode/commands/follow-ticket.md present" 1
else
  check ".opencode/commands/follow-ticket.md missing" 0
fi

# 4. git repo
if git rev-parse --is-inside-work-tree &>/dev/null; then
  check "Inside a git repository" 1
else
  check "Not inside a git repository" 0
fi

# 5. powerhouse dirs
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
for dir in ".internal/.powerhouse/tickets" ".internal/.powerhouse/dispatches" ".internal/.powerhouse/wt"; do
  if [ -d "${REPO_ROOT}/${dir}" ]; then
    check "${dir}/ exists" 1
  else
    mkdir -p "${REPO_ROOT}/${dir}"
    check "${dir}/ created" 1
  fi
done

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "All checks passed. Ready to dispatch."
  exit 0
else
  echo "$ERRORS check(s) failed. Fix the above before running dispatch.sh."
  exit 1
fi
