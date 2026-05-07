#!/usr/bin/env bash
# session-tracking/save.sh
# Save current session state to .session-state
# Run this at the end of each AI chat session.

SESSION_FILE="$(git rev-parse --show-toplevel 2>/dev/null)/.session-state"
if [ -z "$SESSION_FILE" ]; then
  echo "Not in a git repository."
  exit 1
fi

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
MODIFIED=$(git diff --name-only 2>/dev/null | tr '\n' '|')
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | tr '\n' '|')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$SESSION_FILE" <<EOF
LAST_BRANCH=$BRANCH
LAST_COMMIT=$COMMIT
LAST_TIMESTAMP=$TIMESTAMP
MODIFIED_FILES=$MODIFIED
UNTRACKED_FILES=$UNTRACKED
EOF

echo "Session state saved to $SESSION_FILE ($TIMESTAMP)"
