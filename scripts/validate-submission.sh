#!/usr/bin/env bash
set -uo pipefail

PING_URL="${1:-}"
REPO_DIR="${2:-.}"

if [ -z "$PING_URL" ]; then
  echo "Usage: ./validate-submission.sh <ping_url> [repo_dir]"
  exit 1
fi

echo "Step 1: Checking /reset"
curl -X POST "$PING_URL/reset" -H "Content-Type: application/json" -d '{}' || exit 1

echo "Step 2: Docker build"
docker build "$REPO_DIR" || exit 1

echo "Step 3: openenv validate"
openenv validate || exit 1

echo "✅ ALL CHECKS PASSED"