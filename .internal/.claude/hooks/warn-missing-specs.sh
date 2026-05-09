#!/usr/bin/env bash
# Advisory spec-gate: warns when editing a source file in an mcps/ sub-project
# that is missing TECH_SPEC.md or BUILD_STATUS.md.
# Never blocks — always exits 0.
#
# Register in .claude/settings.json PreToolUse for matcher "Edit|Write":
#   {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/warn-missing-specs.sh\""}]}

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only check Edit and Write tool calls
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
  echo '{}'
  exit 0
fi

# Extract file_path from JSON tool input
FILE_PATH=$(printf '%s' "${CLAUDE_TOOL_INPUT:-}" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
[[ -z "$FILE_PATH" ]] && { echo '{}'; exit 0; }

# Skip if the file being edited is a spec file itself
BASENAME="${FILE_PATH##*/}"
if [[ "$BASENAME" == "TECH_SPEC.md" || "$BASENAME" == "BUILD_STATUS.md" ]]; then
  echo '{}'
  exit 0
fi

# Extract sub-project from mcps/<subproject>/... (handles absolute and relative paths)
if [[ "$FILE_PATH" =~ /mcps/([^/]+)/ ]]; then
  SUBPROJECT="${BASH_REMATCH[1]}"
elif [[ "$FILE_PATH" =~ ^mcps/([^/]+)/ ]]; then
  SUBPROJECT="${BASH_REMATCH[1]}"
else
  # Not under mcps/ — skip (.claude/, .powerhouse/, skills/, repo root, etc.)
  echo '{}'
  exit 0
fi

# market-intelligence is exempt: shipped before spec discipline was established
if [[ "$SUBPROJECT" == "market-intelligence" ]]; then
  echo '{}'
  exit 0
fi

# Resolve sub-project root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
SUBPROJECT_ROOT="${REPO_ROOT}/mcps/${SUBPROJECT}"

# Check for each required spec file; warn if missing
for SPEC_FILE in TECH_SPEC.md BUILD_STATUS.md; do
  if [[ ! -f "${SUBPROJECT_ROOT}/${SPEC_FILE}" ]]; then
    echo "[spec-gate] WARNING: mcps/${SUBPROJECT} is missing ${SPEC_FILE} — consider writing the spec first." >&2
  fi
done

echo '{}'
exit 0
