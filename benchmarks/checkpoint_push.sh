#!/usr/bin/env bash
# Spot-instance safety: commit & push benchmark results + logs to GitHub.
# Call this FREQUENTLY (after every task/model) so a preemption never loses progress.
set -uo pipefail
cd /home/serbulentunsal/agentic-bench/repo
export PATH="$HOME/.local/bin:$PATH"
msg="${1:-checkpoint: agentic benchmark progress $(date -u +%FT%TZ)}"
git add -A benchmarks/ 2>/dev/null || true
if git diff --cached --quiet 2>/dev/null; then
  echo "[checkpoint $(date +%H:%M:%S)] nothing new to push"
else
  if git commit -q -m "$msg" && git push -q 2>&1; then
    echo "[checkpoint $(date +%H:%M:%S)] pushed: $msg"
  else
    echo "[checkpoint $(date +%H:%M:%S)] WARNING push failed (will retry next checkpoint)"
  fi
fi
