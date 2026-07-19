#!/usr/bin/env bash
# pst-next.sh — Find first unchecked item across all sub-projects
# Usage: pst-next.sh

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1

FOUND=0

check_file() {
  local label="$1"
  local file="$2"
  if [[ -f "$file" ]]; then
    local unchecked
    unchecked=$(grep -n '\- \[ \]' "$file" | head -3)
    if [[ -n "$unchecked" ]]; then
      echo "=== $label ==="
      echo "$unchecked"
      echo ""
      FOUND=1
    fi
  fi
}

check_file "root" "BUILD_STATUS.md"

for project_dir in mcps/*/; do
  if [[ -d "$project_dir" ]]; then
    name=$(basename "$project_dir")
    check_file "$name" "${project_dir}BUILD_STATUS.md"
  fi
done

if [[ "$FOUND" -eq 0 ]]; then
  echo "All projects: all tasks complete."
fi
