#!/usr/bin/env bash
# detect-project.sh — Infer active sub-project from CWD or --project flag
# Usage: detect-project.sh [--project <name>]
# Returns: project name (e.g., "investment-brain", "market-intelligence", "root")

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"

# Check explicit --project flag
if [[ "$1" == "--project" && -n "$2" ]]; then
  echo "$2"
  exit 0
fi

# Infer from CWD relative to repo root
CWD="$(pwd)"
if [[ "$CWD" == "$REPO_ROOT" ]]; then
  echo "root"
  exit 0
fi

REL="${CWD#$REPO_ROOT/}"
if [[ "$REL" == "$CWD" ]]; then
  echo "root"
  exit 0
fi

# Check mcps/ subdirectory
if [[ "$REL" =~ ^mcps/([^/]+) ]]; then
  echo "${BASH_REMATCH[1]}"
  exit 0
fi

# Check skills/ subdirectory
if [[ "$REL" =~ ^skills/([^/]+) ]]; then
  echo "${BASH_REMATCH[1]}"
  exit 0
fi

echo "root"
