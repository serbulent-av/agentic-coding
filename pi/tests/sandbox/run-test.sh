#!/usr/bin/env bash
#
# run-test.sh — run one live pi delegation test inside the config sandbox.
#
# Mechanism:
#   PI_CODING_AGENT_DIR=/tmp/pi-sandbox makes pi resolve its entire config
#   (settings, agents, workflows, sessions) under /tmp/pi-sandbox instead of
#   ~/.pi/agent, so this run is fully isolated from the real config and writes
#   its session files only into the sandbox (no Docker involved). Run
#   setup-sandbox.sh first.
#
# Usage: run-test.sh dispatch|workflow
#   dispatch  — ask the agentic team directly; the dispatcher should delegate.
#   workflow  — run the saved team-pipeline workflow (requires workflows/
#               to have been built; setup-sandbox.sh copies it if present).
#   Prompts come from prompts.sh (sourced) so both runners stay identical.
#
# Exit code: pi's exit code (from PIPESTATUS). A timed-out/failed pi run is
# reported on stderr but not masked — the log at /tmp/pi-sandbox/last-run.log
# and the session files remain for verify-delegation.py to inspect.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_DIR="/tmp/pi-sandbox"
PROJECT_DIR="/tmp/team-sandbox-proj"
LOG_FILE="$SANDBOX_DIR/last-run.log"
TIMEOUT_SECONDS=1500

# shellcheck source=prompts.sh
source "$SCRIPT_DIR/prompts.sh"

usage() {
    echo "usage: $0 dispatch|workflow" >&2
    exit 2
}

[ $# -eq 1 ] || usage

case "$1" in
    dispatch)
        PROMPT="$DISPATCH_PROMPT"
        ;;
    workflow)
        PROMPT="$WORKFLOW_PROMPT"
        ;;
    *)
        usage
        ;;
esac

if [ ! -d "$SANDBOX_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
    echo "error: sandbox or project missing — run setup-sandbox.sh first" >&2
    exit 2
fi

# Clear state from any prior run so verify-delegation.py inspects only this
# run's sessions (stale sessions once produced a false PASS).
rm -rf "$SANDBOX_DIR/sessions"
mkdir -p "$SANDBOX_DIR/sessions"
rm -f "$LOG_FILE"

export PI_CODING_AGENT_DIR="$SANDBOX_DIR"
cd "$PROJECT_DIR"

set +e
timeout -k 10 "$TIMEOUT_SECONDS" pi -p "$PROMPT" 2>&1 | tee "$LOG_FILE"
PI_EXIT=${PIPESTATUS[0]}
set -e

if [ "$PI_EXIT" -ne 0 ]; then
    if [ "$PI_EXIT" -eq 124 ]; then
        echo "note: pi run TIMED OUT after ${TIMEOUT_SECONDS}s (log kept at $LOG_FILE)" >&2
    else
        echo "note: pi run exited with code $PI_EXIT (log kept at $LOG_FILE)" >&2
    fi
fi
exit "$PI_EXIT"
