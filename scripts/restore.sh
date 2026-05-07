#!/usr/bin/env bash
# session-tracking/restore.sh
# Restore session state from .session-state
# Run this at the start of each new AI chat session.

SESSION_FILE="$(git rev-parse --show-toplevel 2>/dev/null)/.session-state"
if [ -f "$SESSION_FILE" ]; then
  source "$SESSION_FILE"
  echo "=== Previous Session ==="
  echo "  Branch:     $LAST_BRANCH"
  echo "  Commit:     $LAST_COMMIT"
  echo "  Saved at:   $LAST_TIMESTAMP"
  echo "========================"

  # Check if branch still exists
  if git rev-parse --verify "$LAST_BRANCH" >/dev/null 2>&1; then
    echo "  Branch '$LAST_BRANCH' still exists."
    # Show new changes since last save
    NEW=$(git diff --name-only "$LAST_COMMIT"..HEAD 2>/dev/null)
    if [ -n "$NEW" ]; then
      echo "  New changes since last save:"
      echo "$NEW" | sed 's/^/    - /'
    fi
  fi
  echo "========================"
else
  echo "No previous session state found."
  echo "Run tools/save.sh at the end of each chat session to save state."
fi
