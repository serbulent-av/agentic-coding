#!/usr/bin/env bash
#
# run-docker-test.sh — run one live pi delegation test inside a Docker
# container, using the config sandbox built by setup-sandbox.sh.
#
# Mechanism:
#   Same sandbox as run-test.sh (PI_CODING_AGENT_DIR=/tmp/pi-sandbox), but the
#   pi process runs inside the pi-team-sandbox:latest container for stronger
#   isolation: the node runtime (~/.local/share/pi-node/current) and the pi
#   install (~/.pi/agent/install) are bind-mounted READ-ONLY, and the only
#   writable paths the container sees are /tmp/pi-sandbox (config + sessions)
#   and /tmp/team-sandbox-proj (scratch project). Nothing under the real
#   ~/.pi/agent is reachable from inside the container — auth.json enters it
#   only via the sandbox bind mount, and the image itself contains no secrets.
#   The scratch project is mounted at its identical host path
#   (/tmp/team-sandbox-proj) so the shared prompts in prompts.sh, which
#   reference that absolute path, work unchanged in-container.
#
#   The container bypasses the host launcher (~/.pi/agent/bin/pi) and invokes
#   the release binary directly at
#   /pi-install/releases/<version>/node_modules/.bin/pi, with
#   PI_MANAGED_INSTALL_ROOT=/pi-install set so pi detects its managed install
#   correctly. The container runs as the HOST user (--user "$(id -u):$(id -g)",
#   HOME=/tmp) so session files in /tmp/pi-sandbox/sessions are host-owned and
#   verify-delegation.py can read them on the HOST afterwards.
#
# Prerequisites (handled automatically):
#   - image pi-team-sandbox:latest missing  -> runs ./docker-build.sh
#   - /tmp/pi-sandbox missing               -> runs ./setup-sandbox.sh
#
# Usage: run-docker-test.sh dispatch|workflow
#   dispatch  — ask the agentic team directly; the dispatcher should delegate.
#   workflow  — run the saved team-pipeline workflow.
#   Prompts come from prompts.sh (sourced) and are identical to run-test.sh.
#
# Exit code: docker/pi exit code (from PIPESTATUS). A timed-out/failed run is
# reported on stderr but not masked — the log at
# /tmp/pi-sandbox/last-docker-run.log and the session files remain for
# verify-delegation.py to inspect.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="pi-team-sandbox:latest"
SANDBOX_DIR="/tmp/pi-sandbox"
PROJECT_DIR="/tmp/team-sandbox-proj"
LOG_FILE="$SANDBOX_DIR/last-docker-run.log"
TIMEOUT_SECONDS=1500
NODE_RUNTIME_DIR="$HOME/.local/share/pi-node/current"
PI_INSTALL_DIR="$HOME/.pi/agent/install"

# shellcheck source=prompts.sh
source "$SCRIPT_DIR/prompts.sh"

usage() {
    echo "usage: $0 dispatch|workflow" >&2
    exit 2
}

[ $# -eq 1 ] || usage

EXTRA_PI_ARGS=()
case "$1" in
    dispatch)
        PROMPT="$DISPATCH_PROMPT"
        ;;
    workflow)
        PROMPT="$WORKFLOW_PROMPT"
        EXTRA_PI_ARGS=("$WORKFLOW_FLAG")
        ;;
    *)
        usage
        ;;
esac

# --- Prerequisites ----------------------------------------------------------
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "image $IMAGE_NAME not found — building it first" >&2
    "$SCRIPT_DIR/docker-build.sh"
fi

if [ ! -d "$SANDBOX_DIR" ]; then
    echo "sandbox $SANDBOX_DIR missing — running setup-sandbox.sh first" >&2
    "$SCRIPT_DIR/setup-sandbox.sh"
fi

# All remaining bind-mount sources must exist; docker would otherwise create
# an empty host directory (or fail obscurely) on a missing source.
for dir in "$PROJECT_DIR" "$NODE_RUNTIME_DIR" "$PI_INSTALL_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "error: required mount source $dir missing — run setup-sandbox.sh and check your pi install" >&2
        exit 2
    fi
done

# Clear state from any prior run so verify-delegation.py inspects only this
# run's sessions (stale sessions once produced a false PASS).
rm -rf "$SANDBOX_DIR/sessions"
mkdir -p "$SANDBOX_DIR/sessions"
rm -f "$LOG_FILE"

# workflow mode: stage the wrapper next to team-pipeline inside the sandbox
# (the flag path /sandbox-agent/workflows/sandbox-run.js must exist).
if [ "$1" = "workflow" ]; then
    cp "$WORKFLOW_RUNNER" "$SANDBOX_DIR/workflows/sandbox-run.js"
fi

# Release version for the in-container pi binary path. Prefer the host's
# recorded current-version; fall back to the version verified when this
# harness was written.
RELEASE_VERSION="1.6.0"
if [ -f "$PI_INSTALL_DIR/current-version" ]; then
    RELEASE_VERSION="$(cat "$PI_INSTALL_DIR/current-version")"
fi
PI_BIN="/pi-install/releases/$RELEASE_VERSION/node_modules/.bin/pi"

# setup-sandbox.sh symlinks npm/, skills/, bin/, install/ inside the sandbox
# to their absolute host paths under ~/.pi/agent. Those symlinks dangle inside
# the container unless the real agent dir is mounted at its identical host
# path (read-only). Without this mount pi-subagents "fails to install" and the
# run silently degrades to a no-Agent-tool session — a false FAILED test.
REAL_AGENT_DIR="$HOME/.pi/agent"

set +e
if [ "$1" = "workflow" ]; then
    # Workflows run DETACHED in pi-subagents; `pi -p` exits after the first
    # model answer and kills the run (verified: only lange finished, then the
    # completion callback crashed on a stale ctx). So workflow mode starts the
    # pi TUI detached with a pty and polls host-side for completion: the
    # verify command passing plus reviewer sessions present.
    CONTAINER_NAME="pi-team-wf-test"
    HOME_MOUNT="$SANDBOX_DIR/home"
    mkdir -p "$HOME_MOUNT/tmp"
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
    timeout -k 10 "$TIMEOUT_SECONDS" docker run --rm -dit \
        --name "$CONTAINER_NAME" \
        --user "$(id -u):$(id -g)" \
        -e HOME=/home/pitest \
        -e TMPDIR=/home/pitest/tmp \
        -v "$NODE_RUNTIME_DIR:/node:ro" \
        -v "$PI_INSTALL_DIR:/pi-install:ro" \
        -v "$REAL_AGENT_DIR:$REAL_AGENT_DIR:ro" \
        -v "$SANDBOX_DIR:/sandbox-agent" \
        -v "$HOME_MOUNT:/home/pitest" \
        -v "$PROJECT_DIR:$PROJECT_DIR" \
        -e PI_CODING_AGENT_DIR=/sandbox-agent \
        -e PI_MANAGED_INSTALL_ROOT=/pi-install \
        -w "$PROJECT_DIR" "$IMAGE_NAME" \
        "$PI_BIN" "$WORKFLOW_FLAG" > "$LOG_FILE" 2>&1
    DOCKER_EXIT=$?
    if [ $DOCKER_EXIT -ne 0 ]; then
        echo "docker failed to start the workflow container (see $LOG_FILE)" >&2
    else
        echo "workflow container started; polling for completion (verify passes + reviewer sessions)…" >&2
        deadline=$((SECONDS + TIMEOUT_SECONDS))
        done_ok=0
        while [ $SECONDS -lt $deadline ]; do
            # NOTE: session files are JSONL — quotes inside the system prompt
            # are escaped (name=\"sohne\"), so grep for the escaped form or use
            # python on the parsed JSON. Plain 'name="sohne"' never matches.
            review_sessions=$(grep -rl 'active_agent name=..sohne' "$SANDBOX_DIR/sessions" 2>/dev/null | wc -l)
            if [ -f "$PROJECT_DIR/test_textstats.py" ] && (cd "$PROJECT_DIR" && python3 test_textstats.py >/dev/null 2>&1) && [ "$review_sessions" -ge 1 ]; then
                done_ok=1
                break
            fi
            sleep 15
        done
        # let the fix loop / journal flush settle, then stop the TUI
        [ $done_ok -eq 1 ] && sleep 45
        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
        if [ $done_ok -eq 1 ]; then
            echo "workflow completed: verify passes and reviewer sessions present." | tee -a "$LOG_FILE"
            DOCKER_EXIT=0
        else
            echo "workflow did NOT complete within ${TIMEOUT_SECONDS}s — see sessions/journal" | tee -a "$LOG_FILE"
            DOCKER_EXIT=1
        fi
        find "$HOME_MOUNT" -name '*.workflow.jsonl' -exec sh -c 'echo "--- journal: $1"; tail -5 "$1"' _ {} \; | tee -a "$LOG_FILE"
    fi
else
timeout -k 10 "$TIMEOUT_SECONDS" docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$NODE_RUNTIME_DIR:/node:ro" \
    -v "$PI_INSTALL_DIR:/pi-install:ro" \
    -v "$REAL_AGENT_DIR:$REAL_AGENT_DIR:ro" \
    -v "$SANDBOX_DIR:/sandbox-agent" \
    -v "$PROJECT_DIR:$PROJECT_DIR" \
    -e PI_CODING_AGENT_DIR=/sandbox-agent \
    -e PI_MANAGED_INSTALL_ROOT=/pi-install \
    -w "$PROJECT_DIR" "$IMAGE_NAME" \
    "$PI_BIN" "${EXTRA_PI_ARGS[@]}" -p "$PROMPT" 2>&1 | tee "$LOG_FILE"
DOCKER_EXIT=${PIPESTATUS[0]}
fi
set -e

if [ "$DOCKER_EXIT" -ne 0 ]; then
    if [ "$DOCKER_EXIT" -eq 124 ]; then
        echo "note: docker run TIMED OUT after ${TIMEOUT_SECONDS}s (log kept at $LOG_FILE)" >&2
    else
        echo "note: docker run exited with code $DOCKER_EXIT (log kept at $LOG_FILE)" >&2
    fi
fi
exit "$DOCKER_EXIT"
