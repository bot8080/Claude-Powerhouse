#!/usr/bin/env bash
# Dispatch a ticket to OpenCode. On hard failure, hands off to Dev Engineer.
# Usage: bash .powerhouse/dispatch.sh <path-to-ticket.md>
#
# Hard failures (auto Dev Engineer fallback):
#   - opencode binary missing
#   - opencode exits non-zero
#   - zero files changed after OC run
#   - OpenRouter auth missing
#
# Soft failures (prompt user):
#   - OC touched files outside files_to_touch
#   - QA review fails

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# ── Helpers ───────────────────────────────────────────────────────────────────

_log_dispatch() {
  local id="$1" dur="$2" status="$3"
  local ts; ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "| ${ts} | ${id} | opencode/minimax-m2.5-free | ${dur} | ${status} |" >> "${REPO_ROOT}/.powerhouse/dispatch-log.md"
}

_dev_engineer_fallback() {
  local reason="$1"
  echo ""
  echo "── Dev Engineer fallback ────────────────────────────────────────────────"
  echo "  Reason: ${reason}"
  echo ""
  echo "  Original ticket: ${TICKET_PATH}"
  echo "  OC output (if any): ${NDJSON_OUT}"
  echo ""
  echo "  In Claude Code, say:"
  echo "    'Dev Engineer: pick up ticket ${TICKET_PATH}'"
  echo ""
  echo "  Dev Engineer will create a fresh worktree and implement from scratch."
  echo "  QA Engineer reviews the same ticket after Dev Engineer completes."
  echo "──────────────────────────────────────────────────────────────────────────"
}

# ── Validate input ────────────────────────────────────────────────────────────

TICKET_PATH="${1:-}"

if [ -z "$TICKET_PATH" ]; then
  echo "Usage: bash .powerhouse/dispatch.sh <path-to-ticket.md>"
  exit 1
fi

if [ ! -f "$TICKET_PATH" ]; then
  echo "ERROR: Ticket not found: $TICKET_PATH"
  exit 1
fi

# ── Parse ticket frontmatter ──────────────────────────────────────────────────

parse_field() {
  grep -m1 "^${1}:" "$TICKET_PATH" | sed "s/^${1}:[[:space:]]*//"
}

TICKET_ID="$(parse_field id)"
BRANCH="$(parse_field branch)"
FILES_TO_TOUCH="$(awk '/^files_to_touch:/,/^[a-z]/' "$TICKET_PATH" | grep '^ *-' | sed 's/^ *- *//')"

if [ -z "$TICKET_ID" ] || [ -z "$BRANCH" ] || [ -z "$FILES_TO_TOUCH" ]; then
  echo "ERROR: Ticket is missing required fields (id, branch, or files_to_touch)."
  echo "       See .powerhouse/tickets/SCHEMA.md for the required format."
  exit 1
fi

WT="${REPO_ROOT}/.powerhouse/wt/${TICKET_ID}"
NDJSON_OUT="${REPO_ROOT}/.powerhouse/dispatches/${TICKET_ID}.ndjson"

# ── Pre-flight ────────────────────────────────────────────────────────────────

echo ""
echo "→ Dispatch: ticket=${TICKET_ID}  branch=${BRANCH}  model=opencode/minimax-m2.5-free"
echo ""

# Hard failure: opencode not installed
if ! command -v opencode &>/dev/null; then
  echo "HARD FAIL: opencode binary not found."
  echo "  Run: curl -fsSL https://opencode.ai/install | bash"
  _dev_engineer_fallback "opencode not installed"
  exit 0
fi

# Hard failure: OpenRouter not authed
if ! opencode auth list 2>/dev/null | grep -qi openrouter; then
  echo "HARD FAIL: OpenRouter not authenticated."
  echo "  Run: opencode auth login"
  _dev_engineer_fallback "OpenRouter auth missing"
  exit 0
fi

# Reject if worktree already exists
if [ -d "$WT" ]; then
  echo "ERROR: Worktree already exists at ${WT}."
  echo "       Remove it first: git worktree remove ${WT} --force"
  exit 1
fi

# Confirm branch exists
if ! git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  echo "ERROR: Branch '${BRANCH}' does not exist. Create it before dispatching."
  exit 1
fi

# ── Spawn worktree ────────────────────────────────────────────────────────────

echo "Creating worktree at ${WT} ..."
git worktree add "${WT}" "${BRANCH}"

# ── Run OpenCode ──────────────────────────────────────────────────────────────

START_S="$(date +%s)"

echo "Running OpenCode (this may take a few minutes) ..."
echo ""

set +e
(
  cd "${WT}"
  opencode run \
    --model "opencode/minimax-m2.5-free" \
    --quiet \
    --file "${TICKET_PATH}" \
    "/follow-ticket ${TICKET_PATH}"
) > "$NDJSON_OUT" 2>&1
OC_EXIT="$?"
set -e

END_S="$(date +%s)"
DURATION="$((END_S - START_S))s"

# ── Hard failure: OC exited non-zero ─────────────────────────────────────────

if [ "$OC_EXIT" -ne 0 ]; then
  echo "HARD FAIL: opencode exited with code ${OC_EXIT}."
  tail -20 "$NDJSON_OUT"
  _log_dispatch "$TICKET_ID" "$DURATION" "FAIL(exit=${OC_EXIT})"
  _dev_engineer_fallback "opencode exit code ${OC_EXIT}"
  exit 0
fi

# ── Hard failure: zero files changed ─────────────────────────────────────────

CHANGED_FILES="$(git -C "${WT}" diff --name-only HEAD 2>/dev/null || true)"
CHANGED_COUNT="$(echo "$CHANGED_FILES" | grep -c '[^[:space:]]' || true)"

if [ "${CHANGED_COUNT:-0}" -eq 0 ]; then
  echo "HARD FAIL: OpenCode ran but made zero file changes."
  _log_dispatch "$TICKET_ID" "$DURATION" "FAIL(no-changes)"
  _dev_engineer_fallback "OpenCode produced no changes"
  exit 0
fi

# ── Soft failure: files outside files_to_touch ───────────────────────────────

OUT_OF_SCOPE=""
while IFS= read -r changed_file; do
  [ -z "$changed_file" ] && continue
  if ! echo "$FILES_TO_TOUCH" | grep -qF "$changed_file"; then
    OUT_OF_SCOPE="${OUT_OF_SCOPE}  - ${changed_file}"$'\n'
  fi
done <<< "$CHANGED_FILES"

if [ -n "$OUT_OF_SCOPE" ]; then
  echo ""
  echo "SOFT FAIL: OpenCode touched files outside files_to_touch:"
  echo "$OUT_OF_SCOPE"
  echo "Options:"
  echo "  1) Accept anyway — review diff and proceed to QA"
  echo "  2) Hand off to Dev Engineer to clean up"
  echo "  3) Remove worktree and re-dispatch with a revised ticket"
  echo ""
  echo "Worktree preserved at: ${WT}"
  echo "Review diff: git -C '${WT}' diff"
  _log_dispatch "$TICKET_ID" "$DURATION" "SOFT-FAIL(out-of-scope)"
  exit 0
fi

# ── Success ───────────────────────────────────────────────────────────────────

_log_dispatch "$TICKET_ID" "$DURATION" "OK(files=${CHANGED_COUNT})"

echo ""
echo "Dispatch complete."
echo "  Ticket:   ${TICKET_ID}"
echo "  Worktree: ${WT}"
echo "  Changed:  ${CHANGED_COUNT} file(s)"
echo "  Duration: ${DURATION}"
echo ""
echo "Next: say 'review the dispatch' or /powerhouse review to invoke QA Engineer."
