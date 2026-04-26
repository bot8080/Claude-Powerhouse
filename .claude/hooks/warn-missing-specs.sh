#!/bin/bash
# Advisory spec-gate: warns when editing source files in a sub-project that has no TECH_SPEC.md.
# Does NOT block — exits 0 always. Upgrade to blocking by changing the final echo + exit.

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Only check Edit and Write tool calls
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
  echo '{}'
  exit 0
fi

# Extract file path from tool input (JSON field "file_path")
FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
if [[ -z "$FILE_PATH" ]]; then
  echo '{}'
  exit 0
fi

# Exempt: .claude/, skills/, root files, and market-intelligence (pre-spec)
case "$FILE_PATH" in
  */.claude/*|*/skills/*|*market-intelligence*|*.md|*.json|*.sh|*.gitignore)
    echo '{}'
    exit 0
    ;;
esac

# Detect sub-project from file path
SUBPROJECT_DIR=""
if [[ "$FILE_PATH" == */mcps/investment-brain/* ]]; then
  SUBPROJECT_DIR="$REPO_ROOT/mcps/investment-brain"
elif [[ "$FILE_PATH" == */mcps/* ]]; then
  # Other future sub-projects
  SUBPROJECT_DIR=$(echo "$FILE_PATH" | grep -o ".*/mcps/[^/]*" | head -1)
fi

if [[ -z "$SUBPROJECT_DIR" ]]; then
  echo '{}'
  exit 0
fi

# Check for TECH_SPEC.md
if [[ ! -f "$SUBPROJECT_DIR/TECH_SPEC.md" ]]; then
  cat >&2 <<MSG
ADVISORY: No TECH_SPEC.md found in $SUBPROJECT_DIR.

Best practice: write TECH_SPEC.md before editing source files in this sub-project.
  - Define schemas, service signatures, and the build layer map
  - Then run: /powerhouse plan [feature] to get a proper ticket

Proceeding anyway (advisory mode). Set enforce-spec-gate=true in settings to block.
MSG
fi

# Check for BUILD_STATUS.md
if [[ ! -f "$SUBPROJECT_DIR/BUILD_STATUS.md" ]]; then
  cat >&2 <<MSG
ADVISORY: No BUILD_STATUS.md found in $SUBPROJECT_DIR.

Create BUILD_STATUS.md to track layer progress and enable /powerhouse status.
MSG
fi

# Always allow — advisory only
echo '{}'
exit 0
