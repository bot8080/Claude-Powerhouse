#!/usr/bin/env bash
# pst-status.sh — Show current BUILD_STATUS.md layer + next unchecked task
# Usage: pst-status.sh [--project <name>]

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1

PROJECT=$(bash .internal/.powerhouse/lib/detect-project.sh "$@")

if [[ "$PROJECT" == "root" ]]; then
  BUILD_FILE="BUILD_STATUS.md"
else
  BUILD_FILE="mcps/$PROJECT/BUILD_STATUS.md"
fi

if [[ ! -f "$BUILD_FILE" ]]; then
  echo "No BUILD_STATUS.md found for project: $PROJECT"
  exit 1
fi

echo "=== $PROJECT ==="
echo ""

# Find all layer headings
grep -n '^## Layer' "$BUILD_FILE" 2>/dev/null | while IFS=: read -r line heading; do
  echo "$heading"
done

echo ""

# Find first unchecked task
UNCHECKED=$(grep -n '\- \[ \]' "$BUILD_FILE" | head -5)
if [[ -n "$UNCHECKED" ]]; then
  echo "Next unchecked task(s):"
  echo "$UNCHECKED"
else
  echo "All tasks complete."
fi
